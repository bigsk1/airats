import os
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify
from Main import image_url_to_ascii, Image
from io import BytesIO
import requests

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

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
    print("Starting server...")
    print("Please navigate to http://127.0.0.1:8081/ in your browser.")
    app.run(port=8081, debug=True)



