import io
import tempfile
from pathlib import Path
import pytest
from PIL import Image

from engine.agents.media_fetcher import _save_verified_png


def test_save_verified_png_accepts_valid_png():
    # Generate valid 32x32 RGB image in memory
    buf = io.BytesIO()
    img = Image.new("RGB", (32, 32), color=(255, 0, 0))
    img.save(buf, format="PNG")
    valid_png_bytes = buf.getvalue()

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_logo.png"
        result = _save_verified_png(valid_png_bytes, out_path)

        assert result is True
        assert out_path.exists()
        assert out_path.stat().st_size > 0

        # Verify saved file is a valid RGBA PNG
        with Image.open(out_path) as saved_img:
            assert saved_img.format == "PNG"
            assert saved_img.mode == "RGBA"
            assert saved_img.width == 32
            assert saved_img.height == 32


def test_save_verified_png_rejects_svg_bytes():
    svg_bytes = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 22h20L12 2z"/></svg>'
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_logo.png"
        result = _save_verified_png(svg_bytes, out_path)

        assert result is False
        assert not out_path.exists()


def test_save_verified_png_rejects_html_or_corrupt_bytes():
    html_bytes = b"<!DOCTYPE html><html><body><h1>404 Not Found</h1></body></html>"
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_logo.png"
        result = _save_verified_png(html_bytes, out_path)

        assert result is False
        assert not out_path.exists()

    corrupt_bytes = b"\x89PNG\r\n\x1a\ncorrupt"
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_logo.png"
        result = _save_verified_png(corrupt_bytes, out_path)

        assert result is False
        assert not out_path.exists()


def test_save_verified_png_rejects_undersized_image():
    # 8x8 PNG (< 16x16)
    buf = io.BytesIO()
    img = Image.new("RGB", (8, 8), color=(0, 255, 0))
    img.save(buf, format="PNG")
    undersized_bytes = buf.getvalue()

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_logo.png"
        result = _save_verified_png(undersized_bytes, out_path)

        assert result is False
        assert not out_path.exists()
