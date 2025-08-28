import os
import glob
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import rasterio
from rasterio.plot import show
from rasterio.mask import mask
import rioxarray as rxr
import xarray as xr
from pyimpute import impute, load_training_vector, load_targets
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold, GridSearchCV
from sklearn.feature_selection import RFECV
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KernelDensity
from sklearn import model_selection as mod_sel
from sklearn.inspection import partial_dependence
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from scipy.spatial import ConvexHull
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

def clip_rasters_to_presence_extent(
    raster_dir,
    presence_csv,
    lon_col='lon',
    lat_col='lat',
    output_dir='./clipped_rasters',
    buffer_deg=0.1,
    crs_epsg=4326
):
    
    if not os.path.exists(raster_dir):
        raise FileNotFoundError(f"Raster directory not found: {raster_dir}")
    if not os.path.exists(presence_csv):
        raise FileNotFoundError(f"Presence file not found: {presence_csv}")

    # Load presence points
    if presence_csv.endswith('.geojson'):
        pres_df = gpd.read_file(presence_csv)
    else:
        pres_df = gpd.GeoDataFrame(
            pd.read_csv(presence_csv),
            geometry=gpd.points_from_xy(pd.read_csv(presence_csv)[lon_col], pd.read_csv(presence_csv)[lat_col]),
            crs=f"EPSG:{crs_epsg}"
        )

    # Compute bounding box with buffer
    bounds = pres_df.total_bounds
    minx, miny, maxx, maxy = bounds
    minx -= buffer_deg
    miny -= buffer_deg
    maxx += buffer_deg
    maxy += buffer_deg
    bbox = box(minx, miny, maxx, maxy)
    geo = gpd.GeoDataFrame({'geometry': [bbox]}, crs=f"EPSG:{crs_epsg}")
    geo_json = [bbox.__geo_interface__]

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Clip rasters
    for fname in os.listdir(raster_dir):
        if fname.endswith(".tif"):
            print(f"Clipping {fname}")
            input_path = os.path.join(raster_dir, fname)
            output_path = os.path.join(output_dir, fname)
            with rasterio.open(input_path) as src:
                out_image, out_transform = mask(src, geo_json, crop=True)
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)

    print(f"Clipping complete. Rasters saved to: {output_dir}")

def plot_all_tiffs(folder_path):
    
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    tiff_files = glob.glob(os.path.join(folder_path, '*.tif')) + glob.glob(os.path.join(folder_path, '*.tiff'))
    if not tiff_files:
        print("No TIFF files found in the folder.")
        return

    n = len(tiff_files)
    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 5 * nrows))
    axes = axes.flatten() if n > 1 else [axes]

    for idx, tiff_path in enumerate(tiff_files):
        with rasterio.open(tiff_path) as src:
            show(src, ax=axes[idx])
            axes[idx].set_title(os.path.basename(tiff_path))

    for ax in axes[n:]:
        ax.axis('off')

    plt.tight_layout()
    plt.show()

def get_raster_paths_from_folder(raster_dir):
    
    if not os.path.exists(raster_dir):
        raise FileNotFoundError(f"Raster directory not found: {raster_dir}")
    exts = ['.tif', '.tiff']
    return [os.path.join(raster_dir, f) for f in os.listdir(raster_dir) if os.path.splitext(f)[1].lower() in exts]

def stack_rasters(raster_paths):
    
    arrays = []
    meta = None
    for path in raster_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raster file not found: {path}")
        with rasterio.open(path) as src:
            if meta is None:
                meta = src.meta
            arrays.append(src.read(1))
    stack = np.stack(arrays, axis=-1)
    return stack, meta

def raster_to_dataframe(stack, meta):
    
    rows, cols = np.meshgrid(np.arange(meta['height']), np.arange(meta['width']), indexing='ij')
    xs, ys = rasterio.transform.xy(meta['transform'], rows, cols)
    coords = np.column_stack([np.array(xs).flatten(), np.array(ys).flatten()])
    data = stack.reshape(-1, stack.shape[-1])
    df = pd.DataFrame(data, columns=[f'V{i+1}' for i in range(stack.shape[-1])])
    df[['x', 'y']] = coords
    return df.dropna()

def raster_pca(raster_paths, n_components=2, standardize=True, verbose=True):
    
    rasters = [rxr.open_rasterio(p, masked=True).squeeze() for p in raster_paths]
    rasters = [r if "band" in r.dims else r.expand_dims("band") for r in rasters]
    base = rasters[0]
    for i, r in enumerate(rasters[1:], start=1):
        rasters[i] = r.rio.reproject_match(base)
    data = xr.concat(rasters, dim="band")
    data = data.assign_coords(band=[f"B{i+1}" for i in range(data.sizes['band'])])
    data_stacked = data.stack(z=("y", "x"))
    pixel_matrix = data_stacked.transpose("z", "band").values
    valid_rows = ~np.any(np.isnan(pixel_matrix), axis=1)
    pixel_matrix_valid = pixel_matrix[valid_rows]
    scaler = None
    if standardize:
        scaler = StandardScaler()
        pixel_matrix_valid = scaler.fit_transform(pixel_matrix_valid)
    pca = PCA(n_components=n_components)
    pcs = pca.fit_transform(pixel_matrix_valid)
    pc_rasters = np.full((n_components, data.sizes['y'], data.sizes['x']), np.nan)
    idx_flat = np.flatnonzero(valid_rows)
    for i in range(n_components):
        flat = np.full(data.sizes['y'] * data.sizes['x'], np.nan)
        flat[idx_flat] = pcs[:, i]
        pc_rasters[i] = flat.reshape(data.sizes['y'], data.sizes['x'])
    pc_da = xr.DataArray(
        pc_rasters,
        dims=("band", "y", "x"),
        coords={"band": [f"PC{i+1}" for i in range(n_components)], "y": data["y"], "x": data["x"]},
        attrs={"explained_variance": pca.explained_variance_ratio_}
    )
    if verbose:
        print(f"Explained variance: {pca.explained_variance_ratio_}")
    plt.figure(figsize=(8, 6))
    plt.scatter(pcs[:, 0], pcs[:, 1])
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('PCA Plot')
    plt.grid(True)
    plt.show()
    return pc_da, pca, scaler

def estimate_kde_presence(df_pres, bandwidth):
    
    kde = KernelDensity(bandwidth=bandwidth)
    kde.fit(df_pres[['PC1', 'PC2']])
    scores = kde.score_samples(df_pres[['PC1', 'PC2']])
    df_pres['kde'] = np.exp(scores)
    return df_pres, kde

def apply_kde_threshold(df_all, df_pres_kde, threshold):
    
    q = df_pres_kde['kde'].quantile(threshold)
    df_pres_kde['mask'] = np.where(df_pres_kde['kde'] > q, 'in', 'out')
    high_kde_points = df_pres_kde[df_pres_kde['mask'] == 'in'][['PC1', 'PC2']]
    if len(high_kde_points) < 3:
        df_all['mask'] = 'pabs'
        return df_all, set()
    hull = ConvexHull(high_kde_points.values)
    polygon = Polygon(high_kde_points.values[hull.vertices])
    gdf_all = gpd.GeoDataFrame(df_all, geometry=gpd.points_from_xy(df_all['PC1'], df_all['PC2']))
    mask = gdf_all.within(polygon)
    gdf_all['mask'] = np.where(mask, 'in', 'pabs')
    masked_ids = set(gdf_all.loc[mask, 'myID'])
    return gdf_all, masked_ids

def sample_pseudo_absences(df_kde, grid_res_deg, n_samples_per_cell, target_total_absences=None, presence_gdf=None, min_distance_km=5):
    
    df_kde['xcell'] = (df_kde['x'] // grid_res_deg).astype(int)
    df_kde['ycell'] = (df_kde['y'] // grid_res_deg).astype(int)
    sampled = df_kde.groupby(['xcell', 'ycell']).apply(
        lambda g: g.sample(min(len(g), n_samples_per_cell))
    ).reset_index(drop=True)
    if presence_gdf is not None and not presence_gdf.empty:
        presence_union = unary_union(presence_gdf.geometry)
        def far_enough(row):
            point = Point(row['x'], row['y'])
            dist_km = point.distance(presence_union) * 111
            return dist_km >= min_distance_km
        mask = sampled.apply(far_enough, axis=1)
        sampled = sampled[mask].copy()
    if target_total_absences is not None and len(sampled) > target_total_absences:
        sampled = sampled.sample(n=target_total_absences, random_state=42)
    return sampled.reset_index(drop=True)

def generate_random_pseudo_absences(raster_paths, presence_gdf, target_total_absences, min_distance_km=100, grid_res_deg=0.1, n_samples_per_cell=5):
    
    with rasterio.open(raster_paths[0]) as src:
        bounds = src.bounds
        transform = src.transform
    x_coords = np.arange(bounds.left, bounds.right, grid_res_deg)
    y_coords = np.arange(bounds.bottom, bounds.top, grid_res_deg)
    xx, yy = np.meshgrid(x_coords, y_coords)
    all_coords = np.column_stack([xx.flatten(), yy.flatten()])
    df_random = pd.DataFrame(all_coords, columns=['x', 'y'])
    if presence_gdf is not None and not presence_gdf.empty and min_distance_km > 0:
        presence_union = unary_union(presence_gdf.geometry)
        def far_enough(row):
            point = Point(row['x'], row['y'])
            dist_km = point.distance(presence_union) * 111
            return dist_km >= min_distance_km
        mask = df_random.apply(far_enough, axis=1)
        df_random = df_random[mask].copy()
    if len(df_random) > target_total_absences:
        df_random = df_random.sample(n=target_total_absences, random_state=42)
    return df_random.reset_index(drop=True)

def generate_output_filename(base_name, method, ratio, output_dir="."):
    
    method_str = "random" if method.lower() == 'random' else "pca"
    ratio_str = str(ratio).replace('.', '_')
    filename = f"{base_name}_{method_str}_ratio_{ratio_str}.shp"
    return os.path.join(output_dir, filename)

def pseudo_absence_sampling_pca_kde_from_folder(
    raster_dir,
    presence_path,
    method='pca',
    grid_res_deg=0.1,
    threshold=0.75,
    bandwidth=None,
    n_samples_per_cell=5,
    presence_absence_ratio=1,
    min_distance_km=100,
    base_output_name="species_data",
    output_dir=".",
    plot=True
):
    
    if not os.path.exists(raster_dir):
        raise FileNotFoundError(f"Raster directory not found: {raster_dir}")
    if not os.path.exists(presence_path):
        raise FileNotFoundError(f"Presence file not found: {presence_path}")

    output_shapefile = generate_output_filename(base_output_name, method, presence_absence_ratio, output_dir)
    print(f"Using method: {method}")
    print(f"Output will be saved as: {output_shapefile}")

    presence_gdf = gpd.read_file(presence_path)
    target_total_absences = int(len(presence_gdf) * presence_absence_ratio)
    raster_paths = get_raster_paths_from_folder(raster_dir)

    if method.lower() == 'random':
        print("Generating random pseudo-absences...")
        sampled_pa = generate_random_pseudo_absences(
            raster_paths, presence_gdf, target_total_absences,
            min_distance_km=min_distance_km, grid_res_deg=grid_res_deg,
            n_samples_per_cell=n_samples_per_cell
        )
        if sampled_pa.empty:
            print("No pseudo-absence points generated.")
            return None
    else:
        print("Generating PCA-based pseudo-absences...")
        stack, meta = stack_rasters(raster_paths)
        df = raster_to_dataframe(stack, meta)
        df['myID'] = range(len(df))
        pc_da, pca_model, scaler = raster_pca(raster_paths, n_components=2, standardize=True)
        pcs_flat = pc_da.stack(z=("y", "x")).transpose("z", "band").to_pandas()
        pcs_flat.columns = ['PC1', 'PC2']
        pcs_flat[['x', 'y']] = df[['x', 'y']].values
        df = pcs_flat.dropna().copy()
        df['myID'] = range(len(df))
        presence_coords = np.array([[pt.x, pt.y] for pt in presence_gdf.geometry])
        presence_values = []
        for path in raster_paths:
            with rasterio.open(path) as src:
                values = [x[0] for x in src.sample(presence_coords)]
                presence_values.append(values)
        presence_values = np.array(presence_values).T
        presence_df = pd.DataFrame(presence_coords, columns=['x', 'y'])
        presence_df[[f'V{i+1}' for i in range(presence_values.shape[1])]] = presence_values
        if scaler:
            X_pres_std = scaler.transform(presence_df[[f'V{i+1}' for i in range(presence_values.shape[1])]])
        else:
            X_pres_std = presence_df[[f'V{i+1}' for i in range(presence_values.shape[1])]].values
        pcs_pres = pca_model.transform(X_pres_std)
        presence_df[['PC1', 'PC2']] = pcs_pres
        presence_df, kde_model = estimate_kde_presence(presence_df, bandwidth or 1.0)
        gdf_all, masked_ids = apply_kde_threshold(df, presence_df, threshold)
        df_kde = gdf_all[gdf_all['mask'] == 'pabs'].copy()
        if df_kde.empty:
            print("No candidate points left after KDE masking.")
            return None
        sampled_pa = sample_pseudo_absences(df_kde, grid_res_deg, n_samples_per_cell,
                                            target_total_absences=target_total_absences,
                                            presence_gdf=presence_gdf,
                                            min_distance_km=min_distance_km)

    pa_gdf = gpd.GeoDataFrame(sampled_pa, geometry=gpd.points_from_xy(sampled_pa['x'], sampled_pa['y']), crs=presence_gdf.crs)
    if plot:
        fig, ax = plt.subplots(figsize=(10, 8))
        presence_gdf.plot(ax=ax, color='blue', label='Presence', markersize=5, alpha=0.7)
        if not pa_gdf.empty:
            pa_gdf.plot(ax=ax, color='red', alpha=0.5, label='Pseudo-absence', markersize=5)
        ax.legend()
        ax.set_title(f"Presence vs. Pseudo-absence Sampling ({method.upper()} method)")
        plt.show()

    presence_gdf['species'] = 1
    pa_gdf_final = pa_gdf[['x', 'y', 'geometry']].copy()
    pa_gdf_final.columns = ['longitude', 'latitude', 'geometry']
    pa_gdf_final['species'] = 0
    presence_gdf_final = presence_gdf.copy()
    if 'x' in presence_gdf_final.columns:
        presence_gdf_final = presence_gdf_final.rename(columns={'x': 'longitude', 'y': 'latitude'})
    elif 'longitude' not in presence_gdf_final.columns:
        presence_gdf_final['longitude'] = presence_gdf_final.geometry.x
        presence_gdf_final['latitude'] = presence_gdf_final.geometry.y
    presence_absence_df = pd.concat([presence_gdf_final[['longitude', 'latitude', 'geometry', 'species']],
                                     pa_gdf_final], ignore_index=True)
    presence_absence_df.to_file(output_shapefile, driver='ESRI Shapefile')
    print(f"Presence points: {len(presence_gdf)}")
    print(f"Pseudo-absence points: {len(pa_gdf_final)}")
    print(f"Total points: {len(presence_absence_df)}")
    print(f"Data saved to: {output_shapefile}")
    return presence_absence_df

def load_data(pa_path, current_raster_dir, future_raster_dir):
    
    if not os.path.exists(pa_path):
        raise FileNotFoundError(f"Presence-absence file not found: {pa_path}")
    if not os.path.exists(current_raster_dir):
        raise FileNotFoundError(f"Current raster directory not found: {current_raster_dir}")
    if not os.path.exists(future_raster_dir):
        raise FileNotFoundError(f"Future raster directory not found: {future_raster_dir}")
    pa = gpd.read_file(pa_path)
    raster_features = sorted(glob.glob(os.path.join(current_raster_dir, "*.tif")))
    future_rasters = sorted(glob.glob(os.path.join(future_raster_dir, "*.tif")))
    return pa, raster_features, future_rasters

def preprocess_data(pa, raster_features, future_rasters, response_field="species", test_size=0.25):
    
    pa_train, pa_test = train_test_split(pa, test_size=test_size, stratify=pa[response_field])
    train_xs, train_y = load_training_vector(pa_train, raster_features, response_field=response_field)
    target_xs, raster_info = load_targets(raster_features)
    imputer = SimpleImputer(missing_values=np.nan, strategy="mean")
    train_xs = imputer.fit_transform(train_xs)
    target_xs[np.isnan(target_xs)] = 0
    test_xs, test_y = load_training_vector(pa_test, raster_features, response_field=response_field)
    test_target_xs, test_raster_info = load_targets(raster_features)
    test_xs = imputer.fit_transform(test_xs)
    test_target_xs[np.isnan(test_target_xs)] = 0
    target_future, future_raster_info = load_targets(future_rasters)
    target_future[np.isnan(target_future)] = 0
    return train_xs, train_y, test_xs, test_y, target_xs, raster_info, target_future, future_raster_info

def train_and_predict(train_xs, train_y, test_xs, test_y, target_xs, raster_info, output_base_dir, target_future, future_raster_info):
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        CLASS_MAP = {
            "rf": RandomForestClassifier(),
            "et": ExtraTreesClassifier(),
            "xgb": XGBClassifier(),
            "lgbm": LGBMClassifier(verbose=-1)
        }
        trained_models = {}
        for name, model in CLASS_MAP.items():
            k = 5
            kf = mod_sel.KFold(n_splits=k)
            accu_score = mod_sel.cross_val_score(model, train_xs, train_y, cv=kf, scoring="accuracy")
            print(f"{name} CV Accuracy: {accu_score.mean() * 100:.2f} (+/- {accu_score.std() * 200:.2f})")
            accuracy_scores_auc = mod_sel.cross_val_score(model, train_xs, train_y, cv=kf, scoring='roc_auc')
            print(f"{name} CV AUC_ROC: {accuracy_scores_auc.mean() * 100:.2f} (+/- {accuracy_scores_auc.std() * 200:.2f})")
            accuracy_scores_p = mod_sel.cross_val_score(model, train_xs, train_y, cv=kf, scoring='precision')
            print(f"{name} CV Precision: {accuracy_scores_p.mean() * 100:.2f} (+/- {accuracy_scores_p.std() * 200:.2f})")
            accuracy_scores_r = mod_sel.cross_val_score(model, train_xs, train_y, cv=kf, scoring='recall')
            print(f"{name} CV Recall: {accuracy_scores_r.mean() * 100:.2f} (+/- {accuracy_scores_r.std() * 200:.2f})")
            model.fit(train_xs, train_y)
            y_pred = model.predict(test_xs)
            eval1 = confusion_matrix(test_y, y_pred)
            print(f"Confusion Matrix for {name}:\n{eval1}")
            dir_curr = os.path.join(output_base_dir, f'{name}-images')
            os.makedirs(dir_curr, exist_ok=True)
            impute(target_xs, model, raster_info, outdir=dir_curr, class_prob=True, certainty=True)
            dir_fut = os.path.join(output_base_dir, f'{name}-images_future')
            os.makedirs(dir_fut, exist_ok=True)
            impute(target_future, model, future_raster_info, outdir=dir_fut, class_prob=True, certainty=True)
            trained_models[name] = model
        return trained_models

def merged_outcome(output_base_dir, output_name, difference_raster=True):
    
    def read_raster(subdir, filename='probability_1.tif'):
        path = os.path.join(output_base_dir, subdir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing file: {path}")
        return rasterio.open(path).read(1)
    rf = read_raster('rf-images')
    et = read_raster('et-images')
    xgb = read_raster('xgb-images')
    lgbm = read_raster('lgbm-images')
    avg = (rf + et + xgb + lgbm) / 4.0
    meta_path = os.path.join(output_base_dir, 'rf-images', 'probability_1.tif')
    with rasterio.open(meta_path) as src:
        meta = src.meta.copy()
        meta.update(dtype=rasterio.float32)
    output_file = os.path.join(output_base_dir, output_name + '.tif')
    with rasterio.open(output_file, 'w', **meta) as dst:
        dst.write(avg.astype(rasterio.float32), 1)
    print(f"✓ Merged raster saved to: {output_file}")
    if difference_raster:
        fut_rf = read_raster('rf-images_future')
        fut_et = read_raster('et-images_future')
        fut_xgb = read_raster('xgb-images_future')
        fut_lgbm = read_raster('lgbm-images_future')
        avg_fut = (fut_rf + fut_et + fut_xgb + fut_lgbm) / 4.0
        diff = avg_fut - avg
        output_diff_file = os.path.join(output_base_dir, output_name + '_diff.tif')
        with rasterio.open(output_diff_file, 'w', **meta) as dst:
            dst.write(diff.astype(rasterio.float32), 1)
        print(f"Difference raster saved to: {output_diff_file}")
    else:
        print("Difference raster not requested. Only merged output saved.")

def analyze_model(trained_models, feature_names, train_xs):
    
    feature_importances_dfs = {}
    for name, model in trained_models.items():
        print(f"\nAnalyzing Model: {name}")
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
            sorted_importances_df = feature_importance_df.sort_values(by='Importance', ascending=True).reset_index(drop=True)
            print("Feature Importances (Ascending Order):")
            print(sorted_importances_df)
            feature_importances_dfs[name] = sorted_importances_df
        else:
            print("Model does not have feature_importances_ attribute.")
    return feature_importances_dfs

def plot_pdp_with_ci(model, X, feature_names, grid_resolution=20):
    
    X = pd.DataFrame(X, columns=feature_names)
    importances = model.feature_importances_
    top_indices = np.argsort(importances)[::-1][:3]
    top_features = X.columns[top_indices]
    fig, axs = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    all_pdp_results = []
    print(f"Computing PDP for top 3 features...")
    for i, feature in enumerate(top_features):
        pd_result = partial_dependence(model, X, [feature], grid_resolution=grid_resolution, kind="average")
        grid_values = pd_result['grid_values'][0]
        pdp_mean = pd_result['average'][0]
        df_feature = pd.DataFrame({
            'feature': feature,
            'grid_value': grid_values,
            'pdp_mean': pdp_mean
        })
        all_pdp_results.append(df_feature)
        axs[i].plot(grid_values, pdp_mean, label=f'PDP: {feature}', color='blue')
        axs[i].set_xlabel(feature)
        axs[i].set_title(f'Top {i+1}: {feature}')
        axs[i].legend()
    axs[0].set_ylabel("Partial dependence")
    plt.suptitle("Partial Dependence Plots for Top 3 Features")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    return pd.concat(all_pdp_results)

def plotit(output_raster_name, output_dir, title, cmap="Greens", figsize=(6, 5), show_axis=False, cbar_label="Probability", vmin=None, vmax=None, save=False, save_as=None, dpi=300):
    
    raster_path = os.path.join(output_dir, output_raster_name)
    if not os.path.exists(raster_path):
        raise FileNotFoundError(f"Raster file not found: {raster_path}")
    with rasterio.open(raster_path) as src:
        raster = src.read(1)
    plt.figure(figsize=figsize)
    im = plt.imshow(raster, cmap=cmap, interpolation="nearest", vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(im)
    cbar.ax.set_ylabel(cbar_label, rotation=270, labelpad=15)
    plt.title(title, fontweight="bold", fontsize=14)
    if not show_axis:
        plt.xticks([])
        plt.yticks([])
    else:
        plt.xlabel("X")
        plt.ylabel("Y")
    plt.tight_layout()
    if save:
        if save_as is None:
            save_as = os.path.join(output_dir, title.replace(" ", "_") + ".png")
        plt.savefig(save_as, dpi=dpi, bbox_inches="tight")
        print(f"✓ Plot saved to: {save_as}")
    else:
        plt.show()
    plt.close()

def hypertune_model(model, train_xs, train_y, param_grid, cv_k=5):
    
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=cv_k)
    grid_search.fit(train_xs, train_y)
    return grid_search.best_params_, grid_search.cv_results_

def rfe_model(train_xs, train_y, target_xs, feature_names, raster_info):
    
    CLASS_MAP = {
        "rf": RandomForestClassifier(max_depth=6, max_features='sqrt', max_leaf_nodes=6, n_estimators=25),
        "et": ExtraTreesClassifier(),
        "xgb": XGBClassifier(gamma=0.4, learning_rate=0.01, min_child_weight=3, n_estimators=500),
        "lgbm": LGBMClassifier(verbose=-1)
    }
    all_model_results = {}
    for name, model in CLASS_MAP.items():
        rfecv = RFECV(estimator=model, step=1, cv=5, scoring='accuracy', min_features_to_select=2, n_jobs=2)
        rfecv.fit(train_xs, train_y)
        optimal_num_features = rfecv.n_features_
        print(f"Optimal number of features for {name}: {optimal_num_features}")
        selected_features_mask = rfecv.support_
        selected_feature_names = [feature_names[i] for i, selected in enumerate(selected_features_mask) if selected]
        feature_ranking = rfecv.ranking_
        final_model = CLASS_MAP[name]
        final_model.fit(train_xs[:, selected_features_mask], train_y)
        feature_importances = final_model.feature_importances_
        y_pred = final_model.predict(train_xs[:, selected_features_mask])
        y_prob = final_model.predict_proba(train_xs[:, selected_features_mask])[:, 1]
        auc_roc = roc_auc_score(train_y, y_prob)
        feature_importance_with_names = list(zip(selected_feature_names, feature_importances)) if feature_importances is not None and len(selected_feature_names) == len(feature_importances) else None
        all_model_results[name] = {
            'optimal_num_features': optimal_num_features,
            'selected_features_mask': selected_features_mask,
            'feature_ranking': feature_ranking,
            'feature_importance_with_names': feature_importance_with_names,
            'metrics': {'auc_roc': auc_roc}
        }
    return all_model_results
