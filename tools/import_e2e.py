#!/usr/bin/env python3
"""Convert a Heidelberg .e2e file into PNG slices plus JSON metadata.

This helper keeps the C++ side simple by normalizing E2E data into a folder:
  - metadata.json
  - fundus.png (if available)
  - bscan_0000.png, bscan_0001.png, ...

It relies on the third-party `oct-converter` package:
    python -m pip install oct-converter
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def normalize_to_uint8(image):
    import numpy as np

    array = np.asarray(image, dtype="float64")
    if array.size == 0:
        return np.zeros((1, 1), dtype="uint8")

    finite_mask = np.isfinite(array)
    if not finite_mask.any():
        return np.zeros(array.shape, dtype="uint8")

    valid = array[finite_mask]
    min_value = valid.min()
    max_value = valid.max()
    if max_value <= min_value:
        return np.zeros(array.shape, dtype="uint8")

    normalized = (array - min_value) * 255.0 / (max_value - min_value)
    normalized[~finite_mask] = 0.0
    return normalized.clip(0, 255).astype("uint8")


def save_image(path: Path, image) -> None:
    import imageio.v2 as imageio

    imageio.imwrite(path, normalize_to_uint8(image))


def iso_date(value) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def pick_volume(volumes):
    if not volumes:
        return None
    return max(volumes, key=lambda volume: len(volume.volume))


def pick_fundus(fundus_images, laterality):
    if not fundus_images:
        return None
    if laterality:
        for image in fundus_images:
            if getattr(image, "laterality", None) == laterality:
                return image
    return fundus_images[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    try:
        from oct_converter.readers import E2E
    except Exception as exc:  # pragma: no cover - environment dependent
        return fail(
            "Missing dependency `oct-converter`. Install it with "
            "`python -m pip install oct-converter`. Details: {}".format(exc)
        )

    input_file = args.input_file.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        reader = E2E(str(input_file))
        volumes = reader.read_oct_volume()
        fundus_images = reader.read_fundus_image()
    except Exception as exc:
        return fail(f"Failed to parse E2E file: {exc}")

    volume = pick_volume(volumes)
    if volume is None or not volume.volume:
        return fail("No OCT volume data found in the E2E file.")

    width = int(volume.volume[0].shape[1])
    height = int(volume.volume[0].shape[0])
    num_slices = int(len(volume.volume))

    for index, slice_image in enumerate(volume.volume):
        save_image(output_dir / f"bscan_{index:04d}.png", slice_image)

    fundus = pick_fundus(fundus_images, getattr(volume, "laterality", None))
    if fundus is not None:
        save_image(output_dir / "fundus.png", fundus.image)
    else:
        save_image(output_dir / "fundus.png", volume.get_projection())

    pixel_spacing = list(getattr(volume, "pixel_spacing", []) or [])
    while len(pixel_spacing) < 3:
        pixel_spacing.append(None)

    metadata = {
        "input_file": str(input_file),
        "volume_id": getattr(volume, "volume_id", "") or "",
        "patient_id": getattr(volume, "patient_id", "") or "",
        "first_name": getattr(volume, "first_name", "") or "",
        "last_name": getattr(volume, "surname", "") or "",
        "sex": getattr(volume, "sex", "") or "",
        "birth_date": iso_date(getattr(volume, "DOB", None)),
        "acquisition_date": iso_date(getattr(volume, "acquisition_date", None)),
        "laterality": getattr(volume, "laterality", "") or "",
        "width": width,
        "height": height,
        "num_slices": num_slices,
        "pixel_spacing_x_mm": pixel_spacing[0],
        "pixel_spacing_y_mm": pixel_spacing[1],
        "pixel_spacing_z_mm": pixel_spacing[2],
        "bscan_pattern": "bscan_%04d.png",
        "fundus_file": "fundus.png",
    }

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
