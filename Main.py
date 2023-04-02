from PIL import Image

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width)
    return image.resize((new_width, new_height))

def image_to_greyscale(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel // 25]
    return ascii_str

def main():
    image_path = input("Enter the path to the image file: ")
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error: {e}")
        return

    image = resize_image(image)
    greyscale_image = image_to_greyscale(image)
    ascii_pixels = pixels_to_ascii(greyscale_image)
    ascii_image = "\n".join([ascii_pixels[i : i + greyscale_image.width] for i in range(0, len(ascii_pixels), greyscale_image.width)])

    print(ascii_image)

if __name__ == "__main__":
    main()
