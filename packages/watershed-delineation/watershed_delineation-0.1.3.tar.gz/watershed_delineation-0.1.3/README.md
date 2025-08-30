# Watershed Delineation

A Python package for automatic watershed delineation from a Digital Elevation Model (DEM) and a pour point (longitude & latitude).  
It uses [WhiteboxTools](https://github.com/jblindsay/whitebox-tools), [GeoPandas](https://geopandas.org/), and [Rasterio](https://rasterio.readthedocs.io/) to perform hydrologic analysis and export shapefiles with watershed attributes.

---

## 📦 Installation

```bash
pip install watershed-delineation
```

Requirements: Python 3.9 or later. Dependencies like `rasterio` and `geopandas` ship wheels for most platforms, but a recent `pip` is recommended.

---

## 🚀 Usage

### From Python

```python
from watershed_delineation.core import delineate_watershed

# Input parameters
dem_path = r"F:\data\dem.tif"
pour_lon = 32.561170
pour_lat = 39.835840
output_dir = r"C:\results"
watershed_name = "my_basin"

# Run delineation
result_path = delineate_watershed(
    dem_path=dem_path,
    pour_lon=pour_lon,
    pour_lat=pour_lat,
    output_dir=output_dir,
    name=watershed_name,
    buffer_km=50.0,                # buffer half-size in km for DEM clip box
    snap_dist_m=None,              # snapping radius in meters (None = auto)
    snap_multiplier=20,            # multiplier for auto snap distance (default)
    export_lfp=True,               # also export Longest Flow Path
    export_pour_point=True,        # export original pour point (WGS84)
    export_snapped_pour_point=True,# export snapped pour point (DEM CRS)
    export_clip_dem=True,          # export basin-clipped DEM
    export_flow_direction=True,    # export final D8 raster
    export_flow_accumulation=True  # export final FAC raster
)

print("Watershed shapefile saved at:", result_path)
```

WHAT IS "BUFFER SIZE" (buffer_km)?
----------------------------------
During Stage 1 we clip a square around the pour point to keep the DEM small and
processing fast. buffer_km is **half the side length in kilometers** for that
square (so the full square is 2 * buffer_km on each side). A larger buffer
reduces the risk that the watershed extends beyond the clipped area, but takes
longer and uses more memory. Default: 50 km (safe for most basins).

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

---

### From the Command Line

After installation, run:

```bash
delineate_watershed "F:\data\dem.tif" 32.561170 39.835840 -o "C:\results" -n "my_basin" --buffer-km 50 --snap-dist-m 1500 --export-lfp --export-pour-point --export-snapped-pour-point --export-clip-dem --export-flow-direction --export-flow-accumulation
```

Arguments:

- `dem_file` → Path to DEM raster (`.tif`)
- `pour_lon` → Longitude of pour point
- `pour_lat` → Latitude of pour point
- `-o`, `--output` → Output directory (default: current dir)
- `-n`, `--name` → Base name of shapefile (default: watershed_lat_lon)
- `--buffer-km` → Buffer half-side in kilometers (default: 25)
- `--snap-dist-m` → Snap distance in meters (default: None, uses auto)
- `--snap-multiplier` → Multiplier for estimating snap distance (default: 20)
- `--export-lfp` → Export Longest Flow Path shapefile
- `--export-pour-point` → Export input pour point (WGS84)
- `--export-snapped-pour-point` → Export snapped pour point (DEM CRS)
- `--export-clip-dem` → Export basin-clipped DEM
- `--export-flow-direction` → Export final D8 pointer raster
- `--export-flow-accumulation` → Export final flow accumulation raster

---

## 📂 Output

- **`my_basin.shp`** → Watershed polygon shapefile with attributes:
  - Area, perimeter
  - Longest flow path length
  - Form factor, circularity ratio
  - Elevation statistics (min, max, mean)
  - Mean slope
  - Drainage density
  - Pour point coordinates
  - UTM zone metadata for delineation & attributes

- **`my_basin_lfp.shp`** *(optional)* → Longest flow path polyline shapefile  
- **`my_basin_pourpoint_wgs84.shp`** *(optional)* → Input pour point in WGS84  
- **`my_basin_pourpoint_snapped.shp`** *(optional)* → Snapped pour point in DEM CRS  
- **`my_basin_dem_clip_basin.tif`** *(optional)* → Basin-clipped DEM raster  
- **`my_basin_d8.tif`** *(optional)* → Final D8 pointer raster  
- **`my_basin_facc.tif`** *(optional)* → Final flow accumulation raster  

---

## 🛠 Development

Clone and install in editable mode:

```bash
git clone https://github.com/fyec/watershed-delineation.git
cd watershed-delineation
pip install -e .
```

Rebuild after code changes with:

```bash
python -m build
```

---

## 📌 Project Links

- [Homepage](https://github.com/fyec/watershed-delineation)  
- [Bug Tracker](https://github.com/fyec/watershed-delineation/issues)

---

## 👤 Author

Developed by **FYEC**  
Date: August 2025  
License: MIT
