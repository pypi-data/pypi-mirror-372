# -*- coding: utf-8 -*-
"""
Command-line interface for the watershed delineation tool.
"""

import argparse
from pathlib import Path
from watershed_delineation.core import delineate_watershed  # <-- fix

def main():
    parser = argparse.ArgumentParser(
        description="Delineate a watershed from a DEM and a pour point."
    )
    parser.add_argument("dem_file", type=str, help="Path to the input DEM file (.tif).")
    parser.add_argument("pour_lon", type=float, help="Longitude of the pour point (e.g., -122.4194).")
    parser.add_argument("pour_lat", type=float, help="Latitude of the pour point (e.g., 37.7749).")
    parser.add_argument("-o", "--output", type=str, default=".", help="Output directory. Defaults to the current directory.")
    parser.add_argument("-n", "--name", type=str, help="Name for the output shapefile. Defaults to 'watershed_lon_lat'.")
    parser.add_argument("--export-lfp", action="store_true", help="Export the longest flow path as a separate shapefile.")
    args = parser.parse_args()

    dem_path = Path(args.dem_file)
    if not dem_path.is_file():
        print(f"Error: DEM file not found at {dem_path}")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    if args.name:
        name = args.name
    else:
        # (keeps your existing default pattern)
        name = f"watershed_{args.pour_lat}_{args.pour_lon}".replace('.', '_').replace('-', 'm')

    result_path = delineate_watershed(
        dem_path=str(dem_path),
        pour_lon=args.pour_lon,
        pour_lat=args.pour_lat,
        output_dir=str(output_dir),
        name=name,
        export_lfp=args.export_lfp
    )

    if result_path:
        print(f"Final output saved to: {result_path}")
    else:
        print("Delineation failed. See logs for details.")

if __name__ == "__main__":
    main()
