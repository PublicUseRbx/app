from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO
import json

app = Flask(__name__)

WORKER_URL = "https://create2.api-x.site"  # Reemplaza con la URL de tu worker

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

    result = {
        "width": width,
        "height": height,
        "colors": pixel_colors
    }

    # Verificar si se solicita la creación de un archivo en GitHub
    if request.args.get('create_file') == 'true':
        try:
            worker_response = requests.post(WORKER_URL, json=result)
            worker_data = worker_response.json()
            if worker_response.status_code == 200 and worker_data.get('status') == 'success':
                return jsonify({
                    "status": "success",
                    "message": "Archivo creado exitosamente en GitHub",
                    "url": worker_data['url']
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Error al crear el archivo en GitHub",
                    "details": worker_data.get('details', 'Unknown error')
                }), 500
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Error al comunicarse con el worker",
                "details": str(e)
            }), 500
    else:
        return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
