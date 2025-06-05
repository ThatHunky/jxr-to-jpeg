from __future__ import annotations

from pathlib import Path

import imagecodecs
from PIL import Image


def convert_jxr_to_jpeg(src: str | Path, dest: str | Path) -> None:
    """Convert a JXR image to JPEG using the imagecodecs library."""
    src_path = Path(src)
    dest_path = Path(dest)
    data = src_path.read_bytes()
    arr = imagecodecs.jpegxr_decode(data)
    img = Image.fromarray(arr)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_path, format="JPEG")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Convert JXR image to JPEG")
    parser.add_argument("src", help="Input JXR file")
    parser.add_argument("dest", help="Output JPEG file")
    args = parser.parse_args()

    convert_jxr_to_jpeg(args.src, args.dest)


if __name__ == "__main__":
    main()
