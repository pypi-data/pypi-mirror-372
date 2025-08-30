# -*- coding: utf-8 -*-
"""
Core functions for watershed delineation (concise exports).
- Stage 1: delineate basin polygon (no exports here except final .shp)
- Stage 2: compute attributes and (optionally) export final artifacts:
    * LFP (longest flow path)
    * input pour point (WGS84)
    * snapped pour point (DEM CRS)
    * basin-clipped DEM
    * final D8 pointer (within basin)
    * final flow accumulation (within basin)

WHAT IS "BUFFER SIZE" (buffer_km)?
----------------------------------
During Stage 1 we clip a square around the pour point to keep the DEM small and
processing fast. buffer_km is **half the side length in kilometers** for that
square (so the full square is 2 * buffer_km on each side). A larger buffer
reduces the risk that the watershed extends beyond the clipped area, but takes
longer and uses more memory. Default: 100 km (safe for most basins).

WHAT IS "SNAP SIZE" (snap_dist_m / snap_multiplier)?
----------------------------------------------------
Pour points rarely sit exactly on the highest-accumulation cell. We "snap" the
pour point to the cell with the highest flow accumulation within a search
radius. If you **don’t** pass snap_dist_m, we estimate it from the DEM’s pixel
size and multiply by snap_multiplier (default 20). This keeps the search window
proportional to DEM resolution (e.g., for a 30 m DEM → ~600 m default radius).

You can override both:
- Pass buffer_km explicitly to widen/narrow the initial DEM clip.
- Pass snap_dist_m explicitly (in meters) or change snap_multiplier (int).

"""



from pathlib import Path
import os
import shutil
import tempfile
import math
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, box, MultiPolygon
from shapely.ops import unary_union
from pyproj import CRS, Transformer
import rasterio
from rasterio.mask import mask
from whitebox.whitebox_tools import WhiteboxTools


# =============================================================================
# SMALL LOGGING & IO UTILS
# =============================================================================

def _log(msg: str, verbose: bool = True):
    if verbose:
        print(msg)

def _remove_shapefile(path_stem: str):
    """Delete existing shapefile sidecars if present (to avoid driver errors)."""
    exts = [".shp", ".shx", ".dbf", ".prj", ".cpg"]
    for ext in exts:
        p = Path(f"{path_stem}{ext}")
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass

def _safe_write_gdf(gdf: gpd.GeoDataFrame, out_path: str):
    _remove_shapefile(Path(out_path).with_suffix("").as_posix())
    gdf.to_file(out_path)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def utm_crs_from_lonlat(lon: float, lat: float) -> CRS:
    """Determine appropriate UTM zone CRS from lon/lat."""
    zone = int((lon + 180) // 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)

def utm_zone_text_from_epsg(epsg: int) -> str:
    """Return zone string like '36N' from EPSG:32636/32736."""
    if 32601 <= epsg <= 32660:
        return f"{epsg - 32600}N"
    if 32701 <= epsg <= 32760:
        return f"{epsg - 32700}S"
    return "?"

def utm_crs_from_polygon_centroid(poly_gdf: gpd.GeoDataFrame) -> CRS:
    """Determine UTM zone CRS from centroid of polygon GeoDataFrame."""
    wgs = poly_gdf.to_crs(4326)
    c = wgs.geometry.iloc[0].centroid
    zone = int((c.x + 180) // 6) + 1
    epsg = 32600 + zone if c.y >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)

def make_square_box_utm(lon: float, lat: float, half_size_m: float, utm_crs: CRS) -> gpd.GeoDataFrame:
    """Create square polygon buffer in UTM projection."""
    to_utm = Transformer.from_crs(CRS.from_epsg(4326), utm_crs, always_xy=True)
    x, y = to_utm.transform(lon, lat)
    sq = box(x - half_size_m, y - half_size_m, x + half_size_m, y + half_size_m)
    return gpd.GeoDataFrame(geometry=[sq], crs=utm_crs)

def clip_dem_by_polygon(dem_path: str, poly_gdf: gpd.GeoDataFrame, out_path: str) -> str:
    """Clip DEM raster using polygon."""
    with rasterio.open(dem_path) as src:
        dem_crs = src.crs
        if dem_crs is not None:
            poly_gdf = poly_gdf.to_crs(dem_crs)
        out_img, out_transform = mask(src, [poly_gdf.iloc[0].geometry.__geo_interface__], crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_transform
        })
    with rasterio.open(out_path, "w", **out_meta) as dst:
        dst.write(out_img)
    return out_path

def make_pour_point_file(lon: float, lat: float, target_crs: CRS, out_path: str) -> str:
    """Create shapefile for pour point."""
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(lon, lat)], crs="EPSG:4326")
    if target_crs is not None:
        gdf = gdf.to_crs(target_crs)
    _safe_write_gdf(gdf, out_path)
    return out_path

def _assert_exists(path_str: str, step_name: str):
    """Ensure a file exists or raise error."""
    if not Path(path_str).exists():
        raise RuntimeError(f"{step_name} did not produce expected output: {path_str}")

def _meters_per_degree(lat_deg: float):
    """Return (m_per_deg_lon, m_per_deg_lat) at latitude."""
    lat_rad = math.radians(lat_deg)
    m_per_deg_lat = 111320.0
    m_per_deg_lon = math.cos(lat_rad) * 111320.0
    return m_per_deg_lon, m_per_deg_lat

def estimate_snap_distance_m(dem_path: str, pour_lat: float, multiplier: int = 20) -> float:
    """Heuristic snap distance = cell_size_in_m * multiplier (for geographic DEMs converts deg->m)."""
    with rasterio.open(dem_path) as src:
        transform = src.transform
        xres = abs(transform.a)
        yres = abs(transform.e)
        if src.crs and not CRS.from_wkt(src.crs.to_wkt()).is_geographic:
            base_m = max(xres, yres)
        else:
            m_per_deg_lon, m_per_deg_lat = _meters_per_degree(pour_lat)
            base_m = max(xres * m_per_deg_lon, yres * m_per_deg_lat)
    return float(multiplier) * float(base_m)

def snap_point_to_flowacc(pour_pts_vec: str, acc_raster: str, snap_dist_m: float,
                          out_path: str, dem_crs: CRS):
    """Snap pour point to highest accumulation cell within radius."""
    gdf = gpd.read_file(pour_pts_vec)
    if len(gdf) != 1:
        raise RuntimeError(f"Expected 1 pour point, found {len(gdf)}.")
    if gdf.crs is None:
        gdf.crs = dem_crs
    if CRS.from_user_input(gdf.crs) != dem_crs:
        gdf = gdf.to_crs(dem_crs)
    pt = gdf.geometry.iloc[0]
    if pt.is_empty:
        raise RuntimeError("Pour point geometry is empty.")

    with rasterio.open(acc_raster) as src:
        acc = src.read(1)
        transform = src.transform
        nodata = src.nodata
        xres = abs(transform.a)
        yres = abs(transform.e)

        if dem_crs.is_geographic:
            lonlat = gpd.GeoSeries([pt], crs=dem_crs).to_crs("EPSG:4326").iloc[0]
            m_per_deg_lon, m_per_deg_lat = _meters_per_degree(lonlat.y)
            px_m = xres * m_per_deg_lon
            py_m = yres * m_per_deg_lat
        else:
            px_m, py_m = xres, yres

        radius_px = max(1, int(math.ceil(snap_dist_m / max(px_m, py_m))))
        col, row = ~transform * (pt.x, pt.y)
        col, row = int(round(col)), int(round(row))
        r0, r1 = max(0, row - radius_px), min(src.height - 1, row + radius_px)
        c0, c1 = max(0, col - radius_px), min(src.width - 1, col + radius_px)

        window = acc[r0:r1+1, c0:c1+1]
        if window.size == 0:
            raise RuntimeError("Snap window empty; increase SNAP_DIST or check DEM clip.")

        mask_valid = np.ones_like(window, dtype=bool)
        if nodata is not None:
            mask_valid &= (window != nodata)
        mask_valid &= np.isfinite(window)
        if not mask_valid.any():
            raise RuntimeError("No valid accumulation cells in snap window.")

        win_vals = np.where(mask_valid, window, -np.inf)
        idx = np.unravel_index(np.nanargmax(win_vals), win_vals.shape)
        rr, cc = r0 + idx[0], c0 + idx[1]
        x_center, y_center = transform * (cc + 0.5, rr + 0.5)

    out_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[Point(x_center, y_center)], crs=dem_crs)
    _safe_write_gdf(out_gdf, out_path)

def _pick_basin_polygon_from_vectorized(tmp_poly_path: str, snapped_pt_path: str, out_poly_path: str):
    """Select the correct watershed polygon from vectorized output."""
    polys = gpd.read_file(tmp_poly_path)
    if polys.empty:
        raise RuntimeError("Vectorization produced no polygons.")

    value_col = None
    for cand in ["VALUE", "Value", "value", "DN"]:
        if cand in polys.columns:
            value_col = cand
            break

    selected = None
    if value_col is not None:
        pos = polys[polys[value_col].astype(float) > 0]
        if not pos.empty:
            pos = pos.dissolve().explode(index_parts=False).reset_index(drop=True)
            selected = pos

    if selected is None:
        pt = gpd.read_file(snapped_pt_path).geometry.iloc[0]
        pt = gpd.GeoSeries([pt], crs=polys.crs)
        polys["__dist"] = polys.distance(pt.iloc[0])
        polys["__area"] = polys.area
        selected = polys.sort_values(["__dist", "__area"], ascending=[True, False]).head(1)
        selected = selected.drop(columns=["__dist", "__area"], errors="ignore")

    geom = unary_union(selected.geometry)
    if isinstance(geom, MultiPolygon):
        pt = gpd.read_file(snapped_pt_path).geometry.iloc[0]
        parts = list(geom.geoms)
        contains = [p.contains(pt) for p in parts]
        geom = parts[contains.index(True)] if any(contains) else max(parts, key=lambda g: g.area)

    out_gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[geom], crs=polys.crs)
    _safe_write_gdf(out_gdf, out_poly_path)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def delineate_watershed(
    dem_path: str,
    pour_lon: float,
    pour_lat: float,
    output_dir: str,
    name: str,
    export_lfp: bool = False,
    buffer_km: float = 25.0,
    snap_dist_m: float | None = None,
    snap_multiplier: int = 20,
    verbose: bool = True,
    # unified export toggles (all from final/basin stage)
    export_pour_point: bool = False,
    export_snapped_pour_point: bool = False,
    export_clip_dem: bool = False,
    export_flow_direction: bool = False,
    export_flow_accumulation: bool = False,
):
    """
    Delineates watershed and computes attributes; exports are from the final (basin) stage.

    Returns
    -------
    out_poly_shp : str or None
        Path to watershed polygon shapefile, or None if something failed.
    """
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        out_poly_shp = str(Path(output_dir) / f"{name}.shp")

        # Init WBT
        wbt = WhiteboxTools()
        wbt.set_verbose_mode(False)

        # ----- Stage 0: DEM & defaults introspection -----
        _log("▶ Reading DEM and preparing defaults...", verbose)
        with rasterio.open(dem_path) as src:
            dem_crs = CRS.from_wkt(src.crs.to_wkt()) if src.crs else CRS.from_epsg(4326)

        if snap_dist_m is None:
            est = estimate_snap_distance_m(dem_path, pour_lat, multiplier=snap_multiplier)
            snap_dist_m = est
            _log(f"ℹ Snap distance not provided → estimated from DEM cell size × {snap_multiplier}: "
                 f"{snap_dist_m:.1f} m", verbose)
        else:
            _log(f"ℹ Using provided snap distance: {snap_dist_m:.1f} m", verbose)

        _log(f"ℹ Buffer (half-side) for initial DEM clip: {buffer_km:.1f} km", verbose)

        # ----- Delineation (internals) -----
        _log("=== Stage 1: Delineation ===", verbose)
        utm_for_box = utm_crs_from_lonlat(pour_lon, pour_lat)
        utm_box_epsg = int(utm_for_box.to_authority()[1])
        utm_box_zone = utm_zone_text_from_epsg(utm_box_epsg)
        _log(f"• UTM for clip box: {utm_for_box.to_authority()} (zone {utm_box_zone})", verbose)
        _log(f"• Clipping DEM around pour point (lon={pour_lon:.5f}, lat={pour_lat:.5f}, WGS84)...", verbose)

        half = buffer_km * 1000.0
        box_utm = make_square_box_utm(pour_lon, pour_lat, half, utm_for_box)
        box_dem = box_utm.to_crs(dem_crs)

        with tempfile.TemporaryDirectory() as tmp1:
            tmp_path = Path(tmp1)

            clipped_dem_buf = str(tmp_path / "dem_clip_buffer.tif")
            clip_dem_by_polygon(dem_path, box_dem, clipped_dem_buf)

            dem_breached = str(tmp_path / "dem_breached.tif")
            d8_pointer = str(tmp_path / "d8_pointer.tif")   # internal use for watershed()
            facc = str(tmp_path / "flow_acc.tif")           # internal use for snapping
            pour_pts_vec = str(tmp_path / "pour_point_input.shp")
            pour_pts_snap = str(tmp_path / "pour_point_snapped.shp")
            watershed_r = str(tmp_path / "watershed.tif")
            tmp_polys = str(tmp_path / "watershed_polys.shp")

            _log("• Writing initial pour point...", verbose)
            make_pour_point_file(pour_lon, pour_lat, dem_crs, pour_pts_vec)

            _log("• Breaching depressions...", verbose)
            wbt.breach_depressions(dem=clipped_dem_buf, output=dem_breached); _assert_exists(dem_breached, "Breach")

            _log("• D8 pointer & flow accumulation (internal)...", verbose)
            wbt.d8_pointer(dem=dem_breached, output=d8_pointer); _assert_exists(d8_pointer, "D8Pointer")
            wbt.d8_flow_accumulation(i=dem_breached, output=facc, out_type="cells"); _assert_exists(facc, "FlowAccum")

            _log(f"• Snapping pour point to highest-acc within ~{snap_dist_m:.0f} m ...", verbose)
            snap_point_to_flowacc(pour_pts_vec, facc, snap_dist_m, pour_pts_snap, dem_crs)
            _assert_exists(pour_pts_snap, "Snap")

            _log("• Watershed raster from snapped pour point...", verbose)
            wbt.watershed(d8_pntr=d8_pointer, pour_pts=pour_pts_snap, output=watershed_r); _assert_exists(watershed_r, "Watershed")

            _log("• Vectorizing watershed raster and selecting the correct polygon...", verbose)
            wbt.raster_to_vector_polygons(i=watershed_r, output=tmp_polys); _assert_exists(tmp_polys, "Raster2Vector")
            _pick_basin_polygon_from_vectorized(tmp_polys, pour_pts_snap, out_poly_shp)

            # Optional exports for pour points (as requested)
            if export_pour_point:
                out_pp_wgs = str(Path(output_dir) / f"{name}_pourpoint_wgs84.shp")
                _safe_write_gdf(gpd.GeoDataFrame({"id": [1]}, geometry=[Point(pour_lon, pour_lat)], crs="EPSG:4326"), out_pp_wgs)
                _log(f"• Exported input pour point (WGS84) → {out_pp_wgs}", verbose)
            if export_snapped_pour_point:
                snapped = gpd.read_file(pour_pts_snap)
                out_pp_snap = str(Path(output_dir) / f"{name}_pourpoint_snapped.shp")
                _safe_write_gdf(snapped, out_pp_snap)
                _log(f"• Exported snapped pour point → {out_pp_snap}", verbose)

        # ----- Attributes & final exports -----
        _log("=== Stage 2: Attributes ===", verbose)
        with tempfile.TemporaryDirectory() as tmp2:
            tmp_path = Path(tmp2)

            poly_gdf = gpd.read_file(out_poly_shp)
            if poly_gdf.crs is None:
                poly_gdf.crs = dem_crs

            utm_crs = utm_crs_from_polygon_centroid(poly_gdf)
            utm_attr_epsg = int(utm_crs.to_authority()[1])
            utm_attr_zone = utm_zone_text_from_epsg(utm_attr_epsg)
            _log(f"• UTM for basin attributes: {utm_crs.to_authority()} (zone {utm_attr_zone})", verbose)

            poly_utm = poly_gdf.to_crs(utm_crs)
            area_m2 = poly_utm.area.iloc[0]
            perimeter_m = poly_utm.length.iloc[0]
            _log(f"• Basin area ~ {area_m2/1e6:.2f} km²; perimeter ~ {perimeter_m/1000:.2f} km", verbose)

            dem_clip_basin = str(tmp_path / "dem_clip_basin.tif")
            _log("• Clipping DEM to watershed polygon (final/basin)...", verbose)
            clip_dem_by_polygon(dem_path, poly_gdf, dem_clip_basin)

            dem_breached2 = str(tmp_path / "dem_breached2.tif")
            d8_pointer2 = str(tmp_path / "d8_pointer2.tif")
            facc2 = str(tmp_path / "flow_acc2.tif")
            _log("• Breaching / D8 / Flow accumulation (within basin)...", verbose)
            wbt.breach_depressions(dem=dem_clip_basin, output=dem_breached2); _assert_exists(dem_breached2, "Breach2")
            wbt.d8_pointer(dem=dem_breached2, output=d8_pointer2); _assert_exists(d8_pointer2, "D8Pointer2")
            wbt.d8_flow_accumulation(i=dem_breached2, output=facc2, out_type="cells"); _assert_exists(facc2, "FlowAccum2")

            # Longest Flow Path (within basin)
            lfp_vec = str(tmp_path / "lfp.shp")
            _log("• Longest flow path...", verbose)
            wbt.longest_flowpath(dem=dem_breached2, basins=dem_clip_basin, output=lfp_vec); _assert_exists(lfp_vec, "LFP")
            lfp_gdf = gpd.read_file(lfp_vec)
            if lfp_gdf.crs is None:
                lfp_gdf.crs = dem_crs
            lfp_utm = lfp_gdf.to_crs(utm_crs)
            lfp_utm["__len_m"] = lfp_utm.length
            longest_idx = lfp_utm["__len_m"].idxmax()
            lfp_gdf = lfp_gdf.loc[[longest_idx]]
            lfp_length_m = float(lfp_utm.loc[longest_idx, "__len_m"])
            _log(f"• LFP length ~ {lfp_length_m/1000:.2f} km", verbose)

            if export_lfp:
                out_lfp_shp = str(Path(output_dir) / f"{name}_lfp.shp")
                _log(f"• Exporting LFP → {out_lfp_shp}", verbose)
                _safe_write_gdf(lfp_gdf, out_lfp_shp)

            # Optional final exports (single set — all from basin stage)
            if export_clip_dem:
                out = str(Path(output_dir) / f"{name}_dem_clip_basin.tif")
                shutil.copyfile(dem_clip_basin, out)
                _log(f"• Exported basin-clipped DEM → {out}", verbose)
            if export_flow_direction:
                out = str(Path(output_dir) / f"{name}_d8.tif")
                shutil.copyfile(d8_pointer2, out)
                _log(f"• Exported final D8 pointer → {out}", verbose)
            if export_flow_accumulation:
                out = str(Path(output_dir) / f"{name}_facc.tif")
                shutil.copyfile(facc2, out)
                _log(f"• Exported final flow accumulation → {out}", verbose)

            # Shape metrics
            form_factor = area_m2 / (lfp_length_m ** 2) if lfp_length_m > 0 else np.nan
            circularity_ratio = (4 * math.pi * area_m2) / (perimeter_m ** 2) if perimeter_m > 0 else np.nan

            # Elevation & slope stats
            _log("• Elevation and slope statistics...", verbose)
            with rasterio.open(dem_breached2) as src:
                data = src.read(1)
                valid = (data != src.nodata) & np.isfinite(data)
                elev_min  = float(data[valid].min())  if valid.any() else np.nan
                elev_max  = float(data[valid].max())  if valid.any() else np.nan
                elev_mean = float(data[valid].mean()) if valid.any() else np.nan

            slope_raster = str(tmp_path / "slope.tif")
            wbt.slope(dem=dem_breached2, output=slope_raster, units="degrees"); _assert_exists(slope_raster, "Slope")
            with rasterio.open(slope_raster) as src:
                data = src.read(1)
                valid = (data != src.nodata) & np.isfinite(data)
                slope_mean = float(data[valid].mean()) if valid.any() else np.nan

            # Drainage density (simplified)
            _log("• Extracting streams for drainage density (threshold=50 cells)...", verbose)
            streams_raster = str(tmp_path / "streams.tif")
            wbt.extract_streams(flow_accum=facc2, output=streams_raster, threshold=50)
            streams_vec = str(tmp_path / "streams.shp")
            wbt.raster_streams_to_vector(streams=streams_raster, d8_pntr=d8_pointer2, output=streams_vec)

            if Path(streams_vec).exists():
                streams_gdf = gpd.read_file(streams_vec)
                if streams_gdf.crs is None:
                    streams_gdf.crs = dem_crs
                streams_utm = streams_gdf.to_crs(utm_crs)
                total_stream_length_m = float(streams_utm.length.sum())
            else:
                total_stream_length_m = 0.0
            area_km2 = area_m2 / 1e6
            drainage_density = (total_stream_length_m / 1000.0) / area_km2 if area_km2 > 0 else np.nan

            # Save attributes (+ UTM zone info with <=10 char field names)
            _log(f"• Writing attributes to {out_poly_shp}", verbose)
            poly_gdf['area_m2']    = area_m2
            poly_gdf['perim_m']    = perimeter_m
            poly_gdf['lfp_m']      = lfp_length_m
            poly_gdf['form_fact']  = form_factor
            poly_gdf['circ_rat']   = circularity_ratio
            poly_gdf['elev_min']   = elev_min
            poly_gdf['elev_max']   = elev_max
            poly_gdf['elev_mean']  = elev_mean
            poly_gdf['slope_mean'] = slope_mean
            poly_gdf['drain_dens'] = drainage_density
            poly_gdf['pour_lon']   = pour_lon
            poly_gdf['pour_lat']   = pour_lat
            # UTM info (clip-box & basin-attributes)
            poly_gdf['UTMBX_EPSG'] = f"EPSG:{utm_box_epsg}"
            poly_gdf['UTMBX_ZONE'] = utm_box_zone
            poly_gdf['UTMBN_EPSG'] = f"EPSG:{utm_attr_epsg}"
            poly_gdf['UTMBN_ZONE'] = utm_attr_zone

            _safe_write_gdf(poly_gdf, out_poly_shp)

        _log("✅ Done.", verbose)
        return out_poly_shp

    except Exception as e:
        print(f"ERROR: {e}")
        return None
