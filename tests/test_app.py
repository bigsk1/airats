import io
import json
from pathlib import Path
import re
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image

from app import LOCAL_ORIGIN, MAX_COLUMNS, MAX_IMAGE_BYTES, MAX_ROWS, create_app, omarchy_grid


def image_upload(width=16, height=8):
    return upload_image(Image.new("RGB", (width, height), "white"))


def upload_image(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    stream.seek(0)
    return stream, "image.png"


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_conversion_returns_plain_text_with_terminal_proportions(self):
        response = self.client.post("/generate", data={
            "image": image_upload(), "width": "24", "invert": "true",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data.splitlines(), [b"@" * 24] * 6)

    def test_invalid_input_is_rejected(self):
        for data, status in (
            ({"imageUrl": "https://example.test/image.png"}, 400),
            ({"image": (io.BytesIO(b"invalid"), "image.png")}, 400),
            ({"image": image_upload(), "width": "241"}, 400),
            ({"image": image_upload(), "crop_left": "50", "crop_right": "50"}, 400),
            ({"image": image_upload(), "crop_top": "-1"}, 400),
            ({"image": image_upload(), "contrast": "201"}, 400),
            ({"image": image_upload(), "fit_rows": "0"}, 400),
            ({"image": (io.BytesIO(b"0" * (MAX_IMAGE_BYTES + 1)), "large.png")}, 413),
        ):
            with self.subTest(status=status):
                response = self.client.post("/generate", data=data)
                response.request.input_stream.close()
                self.assertEqual(response.status_code, status)

    def test_crop_selects_image_region_and_changes_output_proportions(self):
        image = Image.new("L", (16, 16), 0)
        image.paste(255, (8, 0, 16, 8))
        response = self.client.post("/generate", data={
            "image": upload_image(image), "width": "16", "palette": "minimal",
            "invert": "true", "contrast": "100",
            "crop_left": "50", "crop_top": "0", "crop_right": "0", "crop_bottom": "50",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.splitlines(), [b"#" * 16] * 8)

        response = self.client.post("/generate", data={
            "image": upload_image(image), "width": "16", "crop_left": "50",
        })
        self.assertEqual(len(response.data.splitlines()), 16)

    def test_contrast_changes_character_density(self):
        image = Image.new("L", (2, 2), 80)
        image.paste(180, (1, 0, 2, 2))
        for contrast, expected in (("100", b"+."), ("200", b"# ")):
            with self.subTest(contrast=contrast):
                response = self.client.post("/generate", data={
                    "image": upload_image(image), "width": "2",
                    "palette": "minimal", "contrast": contrast,
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, expected)

    def test_blocks_palette_outputs_utf8_block_gradients(self):
        image = Image.new("L", (5, 2))
        image.putdata([0, 64, 128, 192, 255] * 2)
        response = self.client.post("/generate", data={
            "image": upload_image(image), "width": "5", "palette": "blocks",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "█▓▒░ ")

    def test_screensaver_fit_respects_columns_and_rows_without_cropping(self):
        for size, expected in (((16, 8), (20, 5)), ((16, 96), (6, 18))):
            with self.subTest(size=size):
                response = self.client.post("/generate", data={
                    "image": image_upload(*size), "width": "96", "invert": "true",
                    "fit_columns": "20", "fit_rows": "18",
                })
                self.assertEqual(response.status_code, 200)
                columns, rows = expected
                self.assertEqual(response.data.splitlines(), [b"@" * columns] * rows)

    def test_text_preserves_requested_height_when_it_fits(self):
        request = {
            "mode": "text", "phrase": "bigsk1", "width": "80", "text_rows": "65",
            "fit_columns": "90", "fit_rows": "88", "palette": "blocks",
        }
        response = self.client.post("/generate", data=request)
        lines = response.get_data(as_text=True).splitlines()
        self.assertEqual(response.status_code, 200)
        self.assertEqual([len(line) for line in lines], [80] * 65)
        self.assertIn("█", "".join(lines))
        self.assertIn(" ", "".join(lines))

        fitted = self.client.post("/generate", data={**request, "fit_rows": "22"})
        fitted_lines = fitted.get_data(as_text=True).splitlines()
        self.assertEqual(fitted.status_code, 200)
        self.assertEqual([len(line) for line in fitted_lines], [27] * 22)

    def test_text_strokes_contrast_and_splatter_change_the_artwork(self):
        def render(**settings):
            response = self.client.post("/generate", data={
                "mode": "text", "phrase": "BIG\nsk1", "palette": "blocks", **settings,
            })
            self.assertEqual(response.status_code, 200)
            return response.get_data(as_text=True)

        solid = render()
        outline = render(stroke="outline")
        self.assertLess(len(outline.replace(" ", "")), len(solid.replace(" ", "")))
        self.assertNotEqual(solid, render(contrast="50"))
        self.assertNotEqual(solid, render(lettering="Departure Mono"))
        speckled = render(splatter="75")
        self.assertNotEqual(solid, speckled)
        self.assertEqual(speckled, render(splatter="75"))

    def test_text_rejects_invalid_settings(self):
        for settings in (
            {"phrase": "  "}, {"phrase": "a\nb\nc\nd\ne"}, {"lettering": "../other.ttf"},
            {"text_rows": "1"}, {"fit_rows": "1"}, {"splatter": "101"},
        ):
            with self.subTest(settings=settings):
                response = self.client.post("/generate", data={
                    "mode": "text", "phrase": "bigsk1", **settings,
                })
                self.assertEqual(response.status_code, 400)

    def test_hosted_mode_has_no_install_endpoint(self):
        self.assertEqual(self.client.post("/screensaver").status_code, 404)


class ScreensaverTests(unittest.TestCase):
    def test_screen_grid_accounts_for_scale_rotation_and_multiple_displays(self):
        monitors = [
            {"width": 1920, "height": 1080, "scale": 1.5, "transform": 0},
            {"width": 1920, "height": 1080, "scale": 1, "transform": 1},
            {"width": 640, "height": 480, "scale": 1, "transform": 0, "disabled": True},
        ]
        result = CompletedProcess([], 0, stdout=json.dumps(monitors).encode())
        with (patch("app.subprocess.run", return_value=result),
              patch("app.stock_foot_font", return_value=None)):
            self.assertEqual(omarchy_grid(), (67, 21))

    def test_stock_foot_grid_uses_actual_font_metrics(self):
        monitor = {"width": 1920, "height": 1080, "scale": 1.5, "transform": 0}
        result = CompletedProcess([], 0, stdout=json.dumps([monitor]).encode())
        with (patch("app.subprocess.run", return_value=result),
              patch("app.stock_foot_font", return_value="foot-font.ttf"),
              patch("app.ImageFont.truetype") as font):
            font.return_value.getlength.return_value = 21.6
            font.return_value.getmetrics.return_value = (37, 11)
            self.assertEqual(omarchy_grid(), (87, 22))
            font.assert_called_once_with("foot-font.ttf", 36)

    def test_install_requires_local_origin_and_token_and_backs_up_art(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "screensaver.txt"
            target.write_bytes(b"original\n")
            client = create_app(target).test_client()
            page = client.get("/", base_url=LOCAL_ORIGIN)
            token = re.search(rb'data-token="([^"]+)"', page.data).group(1).decode()
            request_options = {
                "base_url": LOCAL_ORIGIN,
                "content_type": "text/plain",
                "environ_overrides": {"REMOTE_ADDR": "127.0.0.1"},
            }
            headers = {"Origin": LOCAL_ORIGIN, "X-ASCII-Studio-Token": token}
            for bad_headers in ({}, {**headers, "Origin": "https://example.test"}):
                response = client.post("/screensaver", data=b"new art",
                                       headers=bad_headers, **request_options)
                self.assertEqual(response.status_code, 403)
            for invalid_art in (b"\x1b[31m", b"\xff", "█\u200b".encode(),
                                ("█" * (MAX_COLUMNS + 1)).encode()):
                response = client.post("/screensaver", data=invalid_art,
                                       headers=headers, **request_options)
                self.assertEqual(response.status_code, 400)
            self.assertEqual(target.read_bytes(), b"original\n")

            response = client.post("/screensaver", data=b"new art",
                                   headers=headers, **request_options)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(target.read_bytes(), b"new art\n")
            self.assertEqual(target.with_name(response.json["backup"]).read_bytes(), b"original\n")

            blocks = (("█" * MAX_COLUMNS + "\n") * MAX_ROWS).encode()
            response = client.post("/screensaver", data=blocks,
                                   headers=headers, **request_options)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(target.read_bytes(), blocks)
            self.assertEqual(target.with_name(response.json["backup"]).read_bytes(), b"new art\n")
