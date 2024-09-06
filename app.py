from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO
import re

app = Flask(__name__)

@app.route('/<path:image_url>&<dimensions>', methods=['GET'])
def process_image(image_url, dimensions):
    try:
        max_width, max_height = map(int, dimensions.split('x'))
    except ValueError:
        return jsonify({"error": "Invalid dimensions format. Use WIDTHxHEIGHT (e.g., 400x400)"}), 400

    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
    except:
        return jsonify({"error": "Unable to fetch or process the image"}), 400

    img.thumbnail((max_width, max_height))
    width, height = img.size

    pixel_colors = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = img.getpixel((x, y))[:3]
            row.append(f"{r},{g},{b}")
        pixel_colors.append(row)

    return jsonify({
        "width": width,
        "height": height,
        "colors": pixel_colors
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
