from flask import Flask, request, render_template, send_from_directory
import cv2
import numpy as np
import requests
import json
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='.')

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = ''
    text_detected = ''

    if request.method == 'POST':
        file = request.files['image']  # Получение файла из формы
        language = request.form.get('language', 'rus')
        format = request.form.get('format', 'jpg')

        if file:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)  # Сохраняем файл

            # Читаем изображение с помощью OpenCV
            img = cv2.imread(save_path)
            height, width, _ = img.shape
            roi = img[0:height, 0:width]

            # Отправляем изображение на OCR API
            url_api = "https://api.ocr.space/parse/image"
            _, compressed_image = cv2.imencode(f".{format}", roi, [1, 90])
            file_bytes = io.BytesIO(compressed_image)

            result = requests.post(url_api,
                                   files={filename: file_bytes},
                                   data={"apikey": "K87904246888957", "language": language})

            result = result.content.decode()
            result_json = json.loads(result)
            text_detected = result_json.get("ParsedResults")[0].get("ParsedText", "")
            text_detected = text_detected.replace('\r\n', '\n')  # Сохранение отступов

            image_url = f"/{UPLOAD_FOLDER}/{filename}"

    return render_template('index.html', text=text_detected, image_url=image_url)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4567)
