import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from pyproj import Transformer

# 🚀 Configuración de transformación UTM → WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:32718", "EPSG:4326", always_xy=True)

def convertir_utm_a_latlon(geom):
    """Convierte coordenadas UTM (EPSG:32718) a WGS84 (EPSG:4326)."""
    if geom is None:
        return None
    if isinstance(geom, Polygon):
        coords = [(transformer.transform(x, y)) for x, y in geom.exterior.coords]
        return Polygon(coords)
    elif isinstance(geom, MultiPolygon):
        return MultiPolygon([convertir_utm_a_latlon(p) for p in geom.geoms])
    return geom

def cargar_transformar_json(ruta, crs_original="EPSG:32718"):
    """Carga un archivo GeoJSON y transforma las coordenadas a WGS84 si es necesario."""
    gdf = gpd.read_file(ruta)

    # Si el CRS no está definido, asignar el original
    if gdf.crs is None:
        gdf.set_crs(crs_original, inplace=True, allow_override=True)

    # Convertir a WGS84 si no está en ese sistema
    if gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    return gdf

def cargar_datos_excel(ruta):
    """Carga un archivo Excel y filtra solo ID_MANZANA y ValorSuelo."""
    df = pd.read_excel(ruta, usecols=["ID_MANZANA", "ValorSuelo"])
    df["ID_MANZANA"] = df["ID_MANZANA"].astype(str)
    return df

def main():
    print("🚀 Cargando archivos...")

    # 📂 Cargar y transformar datos
    distritos_gdf = cargar_transformar_json("Distritos_Lima.json", crs_original="EPSG:4326")  # Distritos ya están en WGS84
    manzanas_gdf = cargar_transformar_json("manzanas.json")  # Manzanas en UTM, se convierten

    # 📂 Cargar datos del Excel y unirlos con las manzanas
    df_data = cargar_datos_excel("data.xlsx")
    print("🔄 Uniéndo datos de Excel con las manzanas...")
    manzanas_gdf["id_manzana"] = manzanas_gdf["id_manzana"].astype(str)
    df_data.set_index("ID_MANZANA", inplace=True)
    manzanas_gdf = manzanas_gdf.merge(df_data, left_on="id_manzana", right_index=True, how="left")

    # 🔄 Convertir manualmente cada geometría de manzanas a WGS84
    print("🌍 Convirtiendo coordenadas de UTM a WGS84 para manzanas...")
    manzanas_gdf["geometry"] = manzanas_gdf["geometry"].apply(convertir_utm_a_latlon)

    # 🎨 Asignar colores según el valor del suelo
    def asignar_color(valor_suelo):
        if pd.isna(valor_suelo):
            return "gray"
        elif valor_suelo <= 1000:
            return "blue"
        elif valor_suelo <= 3000:
            return "green"
        elif valor_suelo <= 5000:
            return "orange"
        else:
            return "red"

    manzanas_gdf["color"] = manzanas_gdf["ValorSuelo"].apply(asignar_color)

    # 💾 Guardar ambos archivos GeoJSON
    print("💾 Guardando archivos...")
    manzanas_gdf.to_file("static/cached_layers/manzanas_valores_cache.geojson", driver="GeoJSON")
    distritos_gdf.to_file("static/cached_layers/distritos_cache.geojson", driver="GeoJSON")

    print("✅ Archivos generados correctamente.")

if __name__ == "__main__":
    main()
