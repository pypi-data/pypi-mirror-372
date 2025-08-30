#!/usr/bin/env python3
"""
visualize_vector_field.py
-------------------------
CLI tool to visualize 3D vector fields using FURY from a configuration file.
Supports arrow or cylinder visualization, optional VTK export.
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from cardiotensor.colormaps.helix_angle import helix_angle_cmap
from cardiotensor.utils.utils import read_conf_file
from cardiotensor.visualization.vector_field import visualize_vector_field


def script():
    parser = argparse.ArgumentParser(
        description="Plot 3D vector field using FURY from configuration file."
    )
    parser.add_argument("conf_file", type=Path, help="Path to configuration file")
    parser.add_argument(
        "--stride",
        type=int,
        default=10,
        help="Stride to downsample vectors for display (default: 10)",
    )
    parser.add_argument(
        "--bin",
        type=int,
        default=1,
        help="Binning factor used during preprocessing (default: 1)",
    )
    parser.add_argument(
        "--size",
        type=float,
        default=1.0,
        help="Scaling factor for arrows/cylinders (default: 1.0)",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=0.5,
        help="Cylinder radius (ignored if mode=arrow, default: 0.5)",
    )
    parser.add_argument(
        "--mode",
        choices=["arrow", "cylinder"],
        default="arrow",
        help="Visualization mode (default: arrow)",
    )

    parser.add_argument(
        "--colormap",
        type=str,
        default="helix_angle",
        help="Colormap for coloring vectors. "
        "Use 'helix_angle' for custom colormap or any Matplotlib colormap name (default: helix_angle)",
    )

    parser.add_argument("--start", type=int, default=None, help="Start slice index")
    parser.add_argument("--end", type=int, default=None, help="End slice index")
    parser.add_argument(
        "--save", type=Path, help="Optional path to save rendered image"
    )
    parser.add_argument(
        "--vtk", action="store_true", help="Export the vector field to VTK for ParaView"
    )

    args = parser.parse_args()

    # Determine colormap
    if args.colormap.lower() == "helix_angle":
        chosen_cmap = helix_angle_cmap
    else:
        try:
            chosen_cmap = plt.get_cmap(args.colormap)
        except ValueError:
            sys.exit(f"⚠️ Unknown colormap '{args.colormap}'")

    # Read configuration
    params = read_conf_file(args.conf_file)
    output_dir = Path(params.get("OUTPUT_PATH", "./output"))
    voxel_size = params.get("VOXEL_SIZE", 1)
    mask_path = params.get("MASK_PATH", None)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Call visualization function (handles both plotting and VTK export)
    visualize_vector_field(
        vector_field_path=output_dir / "eigen_vec",
        color_volume_path=output_dir / "HA",
        mask_path=mask_path,
        stride=args.stride,
        bin_factor=args.bin,
        size=args.size,
        radius=args.radius,
        mode=args.mode,
        start=args.start,
        end=args.end,
        save_path=args.save,
        voxel_size=voxel_size,
        is_vtk=args.vtk,
        colormap=chosen_cmap,
    )


if __name__ == "__main__":
    script()
