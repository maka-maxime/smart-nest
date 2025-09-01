#!/usr/bin/python3
from flask import Flask, render_template, url_for, send_from_directory
import os
import configparser

app_title = 'IOT - Smart Nest'
app = Flask(app_title)
extensions = {'jpg', 'jpeg'}
config = configparser.ConfigParser()
config.read('config.ini')
picture_folder = config.get('Storage', 'Images')
thumbnail_folder = config.get('Storage', 'Thumbnails')
port = config.get('Network', 'WebPort')

def fetch_images():
    files = []
    for filename in os.listdir(picture_folder):
        if any(filename.lower().endswith(ext) for ext in extensions):
            files.append(filename)
    return files

@app.route('/')
def index():
    images = fetch_images()
    images_data = []

    for img in images:
        image_path = os.path.join(picture_folder, img)
        thumb_path = os.path.join(thumbnail_folder, img)

        images_data.append((
            url_for('send_thumb', filename=img),
            img,
            url_for('send_image', filename=img)
        ))
    return render_template('index.html', title=app_title, images=images_data)

@app.route('/images/<path:filename>')
def send_image(filename):
    return send_from_directory(picture_folder, filename)

@app.route('/thumbnails/<path:filename>')
def send_thumb(filename):
    return send_from_directory(thumbnail_folder, filename)

app.run(host='0.0.0.0', port=port)