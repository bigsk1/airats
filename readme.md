# ASCII Studio

Turn images and words into ASCII art. Upload or crop a photo, or create lettering from a typed phrase. Then copy the artwork, download a text file, or preview it as a screensaver.

## Run locally

Requires Python 3.12 or newer. With [uv](https://docs.astral.sh/uv/) installed, run from the repository root.

```sh
uv run app.py
```

### Manual virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open [ASCII Studio](http://127.0.0.1:5000). On Windows, activate the environment with `.venv\Scripts\Activate.ps1`.

The browser downloads images from URLs. If a site blocks cross-origin access or requires a login, save the image and upload it as a file. The web app accepts JPEG, PNG, GIF, BMP, TIFF, ICO, and WebP files up to 8 MiB and 16 megapixels. It uses the first frame of animated images.

Open **Crop image** and drag a box around the area you want to keep, or enter the percentage to trim from each edge. The ASCII preview updates as you adjust the crop, contrast, width, or character palette. Click **Generate ASCII** to load a pasted URL.

**Balanced** is the default character palette and skips backticks and carets. Try **Dots** for round marks, **Linework** for strokes, or **Blocks** for shaded Unicode characters (`█▓▒░`). **Detailed** is the original palette.

**Preview font** and **Preview color** affect the browser artwork, including the screensaver preview. The bundled faces are Typewriter (Liberation Mono), JetBrains Mono, and Departure Mono. The local Nerd Font option uses an installed JetBrains Mono, Cascadia Code, or Hack Nerd Font when available and falls back to JetBrains Mono. If your Nerd Font is based on JetBrains Mono, the regular letters and punctuation will look similar. Omarchy picks its own terminal font and effects.

## Create text artwork

Select **Text** and type a word or phrase. Use line breaks to stack words. **Lettering font** shapes the letters, and **Character palette** picks the glyphs that draw them. **Text height** and **Width** control the size in rows and columns, so you can stretch or condense the lettering to suit your display.

Choose **Solid** or **Outline**, then adjust **Contrast** to make strokes lighter or denser. **Splatter** adds speckles near the letters. At 0%, the background stays blank.

The screensaver preview centers the lettering horizontally and vertically. For example, **65 rows** on an **88-row** screen leaves 23 rows of vertical space, provided the artwork also fits within the screen’s columns. The app scales the design down proportionally if either dimension exceeds the terminal grid.

## Use your art as an Omarchy screensaver

Run the app directly on your Omarchy desktop as your regular user:

```sh
uv run app.py --omarchy
```

With a manual virtual environment, use `python app.py --omarchy`.

Open [ASCII Studio](http://127.0.0.1:5000), generate artwork and click **Set as Omarchy screensaver**. The app estimates a terminal grid from your active displays using Omarchy's stock font size. Adjust **Columns** and **Rows** if your fullscreen terminal uses a different grid. The preview centers the fitted art on that grid so you can see how much of the screen it will fill.

Click **Install fitted artwork** to save the same text shown in that preview. On compatible Omarchy installations, this saves to `~/.config/omarchy/branding/screensaver.txt` and keeps a uniquely named backup beside it. Launch it immediately with `omarchy launch screensaver force`.

The install button is available in explicit local Omarchy mode. From Docker or a remote instance, download the text file and open the screensaver editor on the desktop with `omarchy branding screensaver text`.

## Command line

```sh
python Main.py images/fish.jpg -w 80 -ht 30 -o artwork.txt
python Main.py https://example.com/image.jpg -w 100 --palette classic --invert
```

Width and height accept 1–240 characters. If you omit the height, it is calculated from the image aspect ratio and the result is fitted within the output limits.

## Docker

```sh
docker build -t ascii-studio .
docker run --rm -p 127.0.0.1:5000:5000 ascii-studio
```

See [LICENSE](LICENSE) for the MIT license. The bundled fonts have their own [Liberation Mono](static/fonts/Liberation-Mono-OFL.txt), [JetBrains Mono](static/fonts/JetBrains-Mono-OFL.txt), and [Departure Mono](static/fonts/Departure-Mono-OFL.txt) licenses.
