from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from PIL import Image

from jxr_to_jpeg import convert_jxr_to_jpeg
import imagecodecs


def test_convert_roundtrip(tmp_path: Path) -> None:
    """Encode an array to JXR then convert to JPEG."""
    data = np.zeros((5, 5, 3), dtype=np.uint8)
    data[0, 0] = [255, 0, 0]
    jxr_bytes = imagecodecs.jpegxr_encode(data)
    src = tmp_path / "sample.jxr"
    dst = tmp_path / "result.jpg"
    src.write_bytes(jxr_bytes)

    convert_jxr_to_jpeg(src, dst)
    img = Image.open(dst)
    assert img.size == (5, 5)
    r, g, b = img.getpixel((0, 0))
    assert r > g and r > b
