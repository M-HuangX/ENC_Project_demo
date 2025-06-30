from flask import Flask, render_template, jsonify, send_file
import os
import json
from datetime import datetime

app = Flask(__name__)

# Config
IMAGE_FOLDER = r'E:\ENC_analysis\ENC_website\data\raw_images'
RESULTS_FOLDER = r'E:\ENC_analysis\ENC_website\data\results'

def get_available_models():
    """Get all available model folders"""
    return [d for d in os.listdir(RESULTS_FOLDER) if os.path.isdir(os.path.join(RESULTS_FOLDER, d))]

def get_latest_json(image_filename, model):
    """Get JSON File"""
    base_name = os.path.splitext(image_filename)[0]
    json_folder = os.path.join(RESULTS_FOLDER, model)
    json_files = [f for f in os.listdir(json_folder) if f.startswith(base_name)]
    if not json_files:
        return None
    return sorted(json_files)[-1]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models')
def get_models():
    return jsonify(get_available_models())

@app.route('/api/files')
def get_files():
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith('.jpg')]
    return jsonify(sorted(image_files))

@app.route('/api/image/<filename>')
def get_image(filename):
    return send_file(os.path.join(IMAGE_FOLDER, filename))

@app.route('/api/json/<model>/<filename>')
def get_json(model, filename):
    if model not in get_available_models():
        return jsonify({"error": "Invalid model"}), 404
    
    json_filename = get_latest_json(filename, model)
    if not json_filename:
        return jsonify({"error": "JSON not found"}), 404
    
    with open(os.path.join(RESULTS_FOLDER, model, json_filename), 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True, port=5000)