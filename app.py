from flask import Flask, render_template, request
import Main

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        image_url = request.form.get("image_url")
        width = int(request.form.get("width"))
        if image_url:
            image = Main.load_image(image_url)
            image = Main.resize_image(image, width)
            greyscale_image = Main.image_to_greyscale(image)
            ascii_pixels = Main.pixels_to_ascii(greyscale_image)
            ascii_image = "\n".join(
                [
                    ascii_pixels[i : i + greyscale_image.width]
                    for i in range(0, len(ascii_pixels), greyscale_image.width)
                ]
            )
            return render_template("index.html", ascii_image=ascii_image)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

