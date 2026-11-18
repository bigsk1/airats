import argparse
from configparser import ConfigParser, Error as ConfigError
import hmac
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile

from flask import Flask, Response, abort, render_template, request, send_from_directory
from PIL import Image, ImageFont

from Main import (
    BLOCK_GLYPHS, DEFAULT_PALETTE, MAX_COLUMNS, MAX_CONTRAST, MAX_IMAGE_BYTES,
    MAX_ROWS, MAX_TEXT_CHARACTERS, MIN_CONTRAST, MIN_TEXT_ROWS, PALETTES,
    TEXT_FONTS, image_url_to_ascii, read_image, text_to_ascii,
)

LOCAL_ORIGIN = "http://127.0.0.1:5000"
BRANDING_FILE = ".config/omarchy/branding/screensaver.txt"
# The supported block glyphs take three bytes each in UTF-8.
MAX_ART_BYTES = (MAX_COLUMNS * 3 + 1) * MAX_ROWS
ART_CHARACTERS = re.compile(rf"[ -~\n{BLOCK_GLYPHS}]+")
DEFAULT_SCREEN_GRID = (80, 24)
SCREEN_CELL_WIDTH = 16
SCREEN_CELL_HEIGHT = 34
SCREEN_CELL_RATIO = SCREEN_CELL_WIDTH / SCREEN_CELL_HEIGHT


def omarchy_target():
    launcher = shutil.which("omarchy-screensaver")
    if sys.platform != "linux" or not launcher or not shutil.which("omarchy"):
        return None
    try:
        if BRANDING_FILE in Path(launcher).read_text(encoding="utf-8"):
            return Path.home() / BRANDING_FILE
    except (OSError, UnicodeError):
        pass
    return None


def stock_foot_font():
    """Resolve the font used by Omarchy's stock Foot screensaver profile."""
    try:
        terminal = subprocess.run(
            ["xdg-terminal-exec", "--print-id"], capture_output=True,
            check=True, text=True, timeout=1,
        )
        if terminal.stdout.strip() != "foot.desktop":
            return None

        root = Path(os.environ.get("OMARCHY_PATH") or "/usr/share/omarchy")
        config = ConfigParser(interpolation=None)
        with (root / "default/foot/screensaver.ini").open(encoding="utf-8") as profile:
            config.read_file(profile)
        settings = config["main"]
        if settings.get("pad") != "0x0" or set(settings) != {"font", "pad"}:
            return None
        if settings["font"] != "JetBrainsMono Nerd Font:size=18":
            return None
        result = subprocess.run(
            ["fc-match", "-f", "%{file}", "JetBrainsMono Nerd Font"],
            capture_output=True, check=True, text=True, timeout=1,
        )
        return result.stdout.strip() or None
    except (OSError, ConfigError, KeyError, subprocess.SubprocessError, ValueError):
        return None


def omarchy_grid():
    """Estimate the shared grid across the active displays."""
    try:
        result = subprocess.run(
            ["hyprctl", "-j", "monitors"], capture_output=True, check=True, timeout=1,
        )
        monitors = json.loads(result.stdout)
        foot_font = stock_foot_font()
        grids = []
        for monitor in monitors:
            if monitor.get("disabled"):
                continue
            width, height = monitor["width"], monitor["height"]
            if monitor["transform"] % 2:
                width, height = height, width
            scale = monitor["scale"]
            # Rounded-up cell dimensions at 96 DPI, expressed in logical pixels.
            columns = int(width / scale // SCREEN_CELL_WIDTH)
            rows = int(height / scale // SCREEN_CELL_HEIGHT)
            if foot_font:
                try:
                    font = ImageFont.truetype(foot_font, max(1, round(24 * scale)))
                    columns = width // math.ceil(font.getlength("0"))
                    rows = height // sum(font.getmetrics())
                except (OSError, ValueError, ZeroDivisionError):
                    pass
            if columns > 0 and rows > 0:
                grids.append((min(MAX_COLUMNS, columns), min(MAX_ROWS, rows)))
        if grids:
            return tuple(map(min, zip(*grids)))
    except (OSError, subprocess.SubprocessError, ValueError, TypeError, KeyError, ZeroDivisionError):
        pass
    return None


def save_screensaver(target, artwork):
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".ascii-studio-",
                                     delete=False) as pending:
        staged = Path(pending.name)
        try:
            pending.write(artwork)
            pending.close()

            backup = None
            try:
                mode = target.lstat().st_mode
            except FileNotFoundError:
                pass
            else:
                if not stat.S_ISREG(mode):
                    raise OSError("The screensaver path must be a regular file.")
                backup = target.with_name(f"{target.name}.{secrets.token_hex(8)}.bak")
                os.link(target, backup)
            staged.replace(target)
            return backup
        finally:
            staged.unlink(missing_ok=True)


def create_app(screensaver_target=None):
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=MAX_IMAGE_BYTES + 65536,
        MAX_FORM_MEMORY_SIZE=512 * 1024,
        MAX_FORM_PARTS=12,
    )
    token = secrets.token_urlsafe(32) if screensaver_target else None
    if token:
        app.config["TRUSTED_HOSTS"] = ["127.0.0.1"]

    @app.after_request
    def secure_response(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' blob:; connect-src 'self' http: https:; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/")
    def index():
        grid = omarchy_grid() if token else None
        response = app.make_response(render_template(
            "index.html", install_token=token, max_columns=MAX_COLUMNS,
            max_rows=MAX_ROWS, min_contrast=MIN_CONTRAST, max_contrast=MAX_CONTRAST,
            palettes=PALETTES, default_palette=DEFAULT_PALETTE,
            screen_grid=grid or DEFAULT_SCREEN_GRID, estimated_grid=grid is not None,
            screen_cell_ratio=SCREEN_CELL_RATIO,
            text_fonts=TEXT_FONTS, min_text_rows=MIN_TEXT_ROWS, max_text=MAX_TEXT_CHARACTERS,
        ))
        if token:
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/sample")
    def sample():
        return send_from_directory(Path(app.root_path) / "images", "fish.jpg")

    @app.post("/generate")
    def generate_ascii():
        mode = request.form.get("mode", "image")
        if mode not in {"image", "text"}:
            return {"error": "Choose image or text."}, 400
        palette = request.form.get("palette", DEFAULT_PALETTE)
        if palette not in PALETTES:
            return {"error": "Choose a character palette."}, 400
        raw_width = request.form.get("width", "96")
        if not re.fullmatch(r"[0-9]{1,3}", raw_width) or not 1 <= int(raw_width) <= MAX_COLUMNS:
            return {"error": f"Enter a width from 1 to {MAX_COLUMNS} columns."}, 400
        contrast = request.form.get("contrast", "100")
        if not re.fullmatch(r"[0-9]{1,3}", contrast):
            return {"error": "Enter a whole percentage for contrast."}, 400
        fit_columns = request.form.get("fit_columns", str(MAX_COLUMNS))
        fit_rows = request.form.get("fit_rows", str(MAX_ROWS))
        screen_fit = "fit_columns" in request.form or "fit_rows" in request.form
        for value, maximum in ((fit_columns, MAX_COLUMNS), (fit_rows, MAX_ROWS)):
            if not re.fullmatch(r"[0-9]{1,3}", value) or not 1 <= int(value) <= maximum:
                return {"error": "Enter a valid terminal grid size."}, 400
        fit = (int(fit_columns), int(fit_rows))

        if mode == "text":
            rows = request.form.get("text_rows", "32")
            splatter = request.form.get("splatter", "0")
            if any(not re.fullmatch(r"[0-9]{1,3}", value) for value in (rows, splatter)):
                return {"error": "Enter whole numbers for text rows and splatter."}, 400
            try:
                artwork = text_to_ascii(
                    request.form.get("phrase", ""), int(raw_width), int(rows), fit=fit,
                    font_name=request.form.get("lettering", "Typewriter"),
                    stroke=request.form.get("stroke", "solid"), contrast=int(contrast),
                    splatter=int(splatter), palette=palette,
                )
            except ValueError as error:
                return {"error": str(error)}, 400
            except OSError:
                app.logger.exception("Could not load the lettering font")
                return {"error": "Could not load the lettering font."}, 500
            return Response(artwork, mimetype="text/plain")

        upload = request.files.get("image")
        if not upload:
            return {"error": "Choose an image to convert."}, 400
        if upload.stream.seek(0, os.SEEK_END) > MAX_IMAGE_BYTES:
            abort(413)
        upload.stream.seek(0)
        crop = [request.form.get(f"crop_{edge}", "0")
                for edge in ("left", "top", "right", "bottom")]
        if any(not re.fullmatch(r"[0-9]{1,2}", value) for value in crop):
            return {"error": "Enter whole percentages from 0 to 99 for the crop edges."}, 400
        try:
            artwork = image_url_to_ascii(
                read_image(upload.stream), int(raw_width), palette=palette,
                invert=request.form.get("invert") == "true",
                cell_ratio=SCREEN_CELL_RATIO if screen_fit else 0.5,
                crop=tuple(map(int, crop)), contrast=int(contrast),
                fit=fit,
            )
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            return {"error": "Choose an image with at most 16 megapixels."}, 400
        except ValueError as error:
            return {"error": str(error)}, 400
        except (OSError, SyntaxError):
            return {"error": "This image is damaged or uses an unsupported format."}, 400
        return Response(artwork, mimetype="text/plain")

    @app.errorhandler(413)
    def too_large(_error):
        if request.endpoint == "install_screensaver":
            return {"error": "The artwork exceeds the screensaver size limit."}, 413
        return {"error": "Choose an image under 8 MiB."}, 413

    if token:
        @app.post("/screensaver")
        def install_screensaver():
            if (request.remote_addr != "127.0.0.1"
                    or request.host_url.rstrip("/") != LOCAL_ORIGIN
                    or request.headers.get("Origin") != LOCAL_ORIGIN
                    or not hmac.compare_digest(
                        request.headers.get("X-ASCII-Studio-Token", "").encode(),
                        token.encode(),
                    )):
                abort(403)
            if request.mimetype != "text/plain":
                abort(415)
            request.max_content_length = MAX_ART_BYTES
            try:
                artwork = request.get_data(cache=False).decode("utf-8").rstrip("\n")
            except UnicodeDecodeError:
                return {"error": "The artwork must use UTF-8 text."}, 400
            rows = artwork.split("\n")
            if (not artwork.strip() or not ART_CHARACTERS.fullmatch(artwork)
                    or len(rows) > MAX_ROWS or any(len(row) > MAX_COLUMNS for row in rows)):
                return {"error": "Generate a valid scene before installing."}, 400
            try:
                backup = save_screensaver(screensaver_target, (artwork + "\n").encode("utf-8"))
            except OSError:
                app.logger.exception("Could not save screensaver")
                return {"error": "Could not write the Omarchy screensaver file. Check its permissions."}, 500
            return {"backup": backup.name if backup else None}

    return app


app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ASCII Studio locally.")
    parser.add_argument("--omarchy", action="store_true", help="Enable local screensaver installation.")
    args = parser.parse_args()
    target = omarchy_target() if args.omarchy else None
    if args.omarchy and not target:
        parser.exit(1, "This Omarchy installation's screensaver file could not be detected.\n")
    create_app(target).run(host="127.0.0.1", port=5000, debug=False, threaded=False)
