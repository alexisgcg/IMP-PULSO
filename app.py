import os
import logging
from flask import Flask, jsonify, send_from_directory, render_template

app = Flask(__name__)

CACHE_DIR = os.path.join("static", "cached_layers")

@app.route('/geojson/<layer>')
def get_geojson(layer):
    filepath = os.path.join(CACHE_DIR, f"{layer}.geojson")
    if not os.path.exists(filepath):
        return jsonify({"error": f"Archivo {layer} no encontrado."}), 404
    return send_from_directory(CACHE_DIR, f"{layer}.geojson", mimetype='application/json')

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
