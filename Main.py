import argparse
from io import BytesIO
from math import ceil, floor
from pathlib import Path
from random import Random
import warnings

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000
MAX_COLUMNS = 240
MAX_ROWS = 240
MIN_CONTRAST = 50
MAX_CONTRAST = 200
IMAGE_FORMATS = ("JPEG", "PNG", "GIF", "BMP", "TIFF", "ICO", "WEBP")
DEFAULT_PALETTE = "balanced"
BLOCK_GLYPHS = "█▓▒░"
PALETTES = {
    "balanced": "@%#WM8&$O0oQCLJYXzcvunxrjft+=~-:,. ",
    "dots": "@O0o*+:. ",
    "linework": "#%Xx+|/\\:-. ",
    "blocks": BLOCK_GLYPHS + " ",
    "classic": "@%#*+=-:. ",
    "minimal": "#+-. ",
    "detailed": "@B%8WM#*oahkbdpqwmZO0QLCJYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
}
TEXT_FONTS = {
    "Typewriter": "LiberationMono-Regular.ttf",
    "JetBrains Mono": "JetBrainsMono-Regular.woff2",
    "Departure Mono": "DepartureMono-Regular.woff2",
}
FONT_DIR = Path(__file__).resolve().parent / "static/fonts"
MAX_TEXT_CHARACTERS = 100
MAX_TEXT_LINES = 4
MIN_TEXT_ROWS = 8


def read_image(source):
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(source, formats=IMAGE_FORMATS) as image:
            validate_image_size(image)
            return ImageOps.exif_transpose(image)


def validate_image_size(image):
    if image.width * image.height > MAX_IMAGE_PIXELS:
        raise ValueError("Choose an image with at most 16 megapixels.")


def image_url_to_ascii(image, new_width, new_height=None, *, palette=DEFAULT_PALETTE,
                       invert=False, cell_ratio=1, crop=(0, 0, 0, 0), contrast=100,
                       fit=(MAX_COLUMNS, MAX_ROWS)):
    validate_image_size(image)
    if not 1 <= new_width <= MAX_COLUMNS:
        raise ValueError(f"Width must be between 1 and {MAX_COLUMNS} columns.")
    if not MIN_CONTRAST <= contrast <= MAX_CONTRAST:
        raise ValueError(f"Contrast must be between {MIN_CONTRAST}% and {MAX_CONTRAST}%.")
    left, top, right, bottom = crop
    if (any(edge < 0 for edge in crop) or left + right >= 100 or top + bottom >= 100):
        raise ValueError("Leave some of the image visible on both axes.")
    if any(crop):
        x0 = image.width * left // 100
        y0 = image.height * top // 100
        x1 = image.width - image.width * right // 100
        y1 = image.height - image.height * bottom // 100
        image = image.crop((x0, y0, x1, y1))
    if new_height is None:
        fit_columns, fit_rows = fit
        new_width = min(new_width, fit_columns)
        new_height = max(1, round(image.height / image.width * new_width * cell_ratio))
        if new_height > fit_rows:
            new_width = max(1, round(new_width * fit_rows / new_height))
            new_height = fit_rows
    if not 1 <= new_height <= MAX_ROWS:
        raise ValueError(f"Height must be between 1 and {MAX_ROWS} rows.")

    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    if "A" in resized.getbands() or "transparency" in resized.info:
        overlay = resized.convert("RGBA")
        background = Image.new("RGBA", overlay.size, "black" if invert else "white")
        resized = Image.alpha_composite(background, overlay)
    grayscale = resized.convert("L")
    if contrast != 100:
        grayscale = ImageEnhance.Contrast(grayscale).enhance(contrast / 100)
    return grayscale_to_ascii(grayscale, palette, invert)


def grayscale_to_ascii(grayscale, palette, invert=False):
    characters = PALETTES[palette]
    if invert:
        characters = characters[::-1]
    table = {pixel: characters[pixel * len(characters) // 256] for pixel in range(256)}
    art = grayscale.tobytes().decode("latin-1").translate(table)
    return "\n".join(art[i:i + grayscale.width] for i in range(0, len(art), grayscale.width))


def text_to_ascii(text, width, rows, *, font_name, stroke, contrast, splatter, palette, fit):
    text = text.replace("\r\n", "\n").strip()
    if not text or len(text) > MAX_TEXT_CHARACTERS or text.count("\n") >= MAX_TEXT_LINES:
        raise ValueError(f"Enter up to {MAX_TEXT_CHARACTERS} characters on {MAX_TEXT_LINES} lines.")
    if any(not line.isprintable() for line in text.split("\n") if line):
        raise ValueError("Use printable characters or line breaks.")
    if font_name not in TEXT_FONTS or stroke not in {"solid", "outline"}:
        raise ValueError("Choose a lettering font and stroke style.")
    if not MIN_TEXT_ROWS <= rows <= MAX_ROWS or not 0 <= splatter <= 100:
        raise ValueError(f"Choose {MIN_TEXT_ROWS}–{MAX_ROWS} text rows and 0–100% splatter.")
    if not MIN_CONTRAST <= contrast <= MAX_CONTRAST:
        raise ValueError(f"Contrast must be between {MIN_CONTRAST}% and {MAX_CONTRAST}%.")

    scale = min(1, fit[0] / width, fit[1] / rows)
    width, rows = max(1, round(width * scale)), round(rows * scale)
    if width < 2 or rows < 2:
        raise ValueError("The fitted lettering needs at least two columns and two rows.")

    font = ImageFont.truetype(FONT_DIR / TEXT_FONTS[font_name], 128)
    draw_options = dict(font=font, spacing=20, align="center", stroke_width=6)
    bounds = ImageDraw.Draw(Image.new("L", (1, 1))).multiline_textbbox((0, 0), text, **draw_options)
    left, top, right, bottom = bounds
    origin = (-floor(left), -floor(top))
    stencil = Image.new("L", (ceil(right) + origin[0], ceil(bottom) + origin[1]))
    ImageDraw.Draw(stencil).multiline_text(origin, text, fill=255, **draw_options)
    ink_bounds = stencil.getbbox()
    if not ink_bounds:
        raise ValueError("The selected font could not draw that text.")
    letters = stencil
    if stroke == "outline":
        letters = Image.new("L", stencil.size)
        ImageDraw.Draw(letters).multiline_text(origin, text, fill=0, stroke_fill=255, **draw_options)

    # Reserve a narrow border for speckles without changing the selected grid size.
    margin = min(ceil(splatter * 3 / 100), (min(width, rows) - 2) // 4)
    inner_size = (width - margin * 2, rows - margin * 2)
    cells = Image.new("L", (width, rows))
    cells.paste(letters.crop(ink_bounds).resize(inner_size, Image.Resampling.BOX), (margin, margin))
    edge_cutoff = 12
    gain = 255 / (255 - edge_cutoff) * contrast / 100
    density = cells.point(lambda p: min(255, max(0, round((p - edge_cutoff) * gain))))
    if splatter:
        silhouette = Image.new("L", cells.size)
        silhouette.paste(stencil.crop(ink_bounds).resize(inner_size, Image.Resampling.BOX), (margin, margin))
        neighborhood = silhouette.filter(ImageFilter.MaxFilter(7))
        rng = Random(text)
        pixels = bytearray(density.tobytes())
        for i, (letter, nearby) in enumerate(zip(silhouette.tobytes(), neighborhood.tobytes())):
            if not pixels[i] and letter < edge_cutoff and nearby > 80:
                chance, strength = rng.random(), rng.randint(65, 130)
                if chance < splatter / 400:
                    pixels[i] = strength
        density = Image.frombytes("L", cells.size, bytes(pixels))
    return grayscale_to_ascii(ImageOps.invert(density), palette)


def load_image(image_source):
    if image_source.startswith(("http://", "https://")):
        with requests.get(image_source, stream=True, timeout=(5, 10)) as response:
            response.raise_for_status()
            data = BytesIO()
            for chunk in response.iter_content(chunk_size=65536):
                if data.tell() + len(chunk) > MAX_IMAGE_BYTES:
                    raise ValueError("Choose an image under 8 MiB.")
                data.write(chunk)
            data.seek(0)
            return read_image(data)
    with open(image_source, "rb") as source:
        return read_image(source)


def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art.")
    parser.add_argument("image_source", help="Local path or HTTP(S) image URL.")
    parser.add_argument("-w", "--width", type=int, default=100)
    parser.add_argument("-ht", "--height", type=int)
    parser.add_argument("-o", "--output", help="Path to save the ASCII output.")
    parser.add_argument("--palette", choices=PALETTES, default=DEFAULT_PALETTE)
    parser.add_argument("--invert", action="store_true")
    args = parser.parse_args()

    try:
        artwork = image_url_to_ascii(load_image(args.image_source), args.width, args.height,
                                    palette=args.palette, invert=args.invert)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as output:
                output.write(artwork)
        else:
            print(artwork)
    except (OSError, ValueError, requests.RequestException, UnidentifiedImageError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        parser.exit(1, f"Could not convert image: {error}\n")


if __name__ == "__main__":
    main()
