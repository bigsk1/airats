from flask import Flask, render_template, request, jsonify
from PIL import Image
from io import BytesIO
import requests
import logging

logging.basicConfig(filename='airats.log', level=logging.WARNING)

from Main import image_url_to_ascii  # Import the function from Main.py

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_ascii():
    data = request.get_json()
    image_url = data.get('imageUrl')
    width = int(data.get('width'))

    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        ascii_art = image_url_to_ascii(image, width)
        return ascii_art
    except Exception as e:
        print(e)
        return 'Error generating ASCII art', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

