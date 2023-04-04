import sys
import argparse
import requests
from PIL import Image
from io import BytesIO

ASCII_CHARS = ["@", "B", "%", "8", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", "\"", "^", "`", "'", ".", " "]

def resize_image(image, new_width=100, new_height=None):
    width, height = image.size
    if new_height is None:
        aspect_ratio = height / width
        new_height = int(aspect_ratio * new_width)
    return image.resize((new_width, new_height))

def image_to_greyscale(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
    return ascii_str

def load_image(image_source):
    if image_source.startswith("http://") or image_source.startswith("https://"):
        response = requests.get(image_source)
        try:
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        try:
            return Image.open(image_source)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII art.")
    parser.add_argument("image_source", help="Path or URL to the input image.")
    parser.add_argument("-w", "--width", type=int, default=100, help="Output width of the ASCII image. Default is 100.")
    parser.add_argument("-ht", "--height", type=int, default=None, help="Output height of the ASCII image. If not specified, it will be calculated based on the aspect ratio.")
    parser.add_argument("-o", "--output", help="Path to save the ASCII output. If not specified, the output will be printed on the console.")

    args = parser.parse_args()

    image = load_image(args.image_source)
    image = resize_image(image, args.width, args.height)
    greyscale_image = image_to_greyscale(image)
    ascii_pixels = pixels_to_ascii(greyscale_image)
    ascii_image = "\n".join([ascii_pixels[i : i + greyscale_image.width] for i in range(0, len(ascii_pixels), greyscale_image.width)])

    if args.output:
        with open(args.output, "w") as f:
            f.write(ascii_image)
    else:
        print(ascii_image)

if __name__ == "__main__":
    main()