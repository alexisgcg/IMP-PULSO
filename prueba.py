import json

with open("static/cached_layers/manzanas_valores_cache.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Obtener las primeras coordenadas
primeras_coordenadas = data["features"][0]["geometry"]["coordinates"][0]
print("Primeras coordenadas de la primera manzana:", primeras_coordenadas)
