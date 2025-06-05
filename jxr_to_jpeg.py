from __future__ import annotations

from pathlib import Path

import imagecodecs
from PIL import Image


HDR_P3_PROFILE = Path(__file__).with_name("hdr_p3.icc")


def convert_jxr_to_jpeg(
    src: str | Path, dest: str | Path, icc_profile: str | Path | None = None
) -> None:
    """Convert a JXR image to JPEG using the imagecodecs library."""
    src_path = Path(src)
    dest_path = Path(dest)
    data = src_path.read_bytes()
    arr = imagecodecs.jpegxr_decode(data)
    img = Image.fromarray(arr)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs = {"format": "JPEG"}
    if icc_profile:
        save_kwargs["icc_profile"] = Path(icc_profile).read_bytes()
    img.save(dest_path, **save_kwargs)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Convert JXR image to JPEG")
    parser.add_argument("src", help="Input JXR file")
    parser.add_argument("dest", help="Output JPEG file")
    parser.add_argument(
        "--hdr-p3",
        action="store_true",
        help="Embed the included HDR P3 color profile in the output JPEG",
    )
    args = parser.parse_args()

    profile = HDR_P3_PROFILE if args.hdr_p3 else None
    convert_jxr_to_jpeg(args.src, args.dest, icc_profile=profile)


if __name__ == "__main__":
    main()
