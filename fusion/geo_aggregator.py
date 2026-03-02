import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from fusion.h3_mapper import get_hex_boundary

def aggregate_scores_to_gdf(scores: list[dict]) -> gpd.GeoDataFrame:
    """Converts a list of dict scores to a GeoDataFrame with hexagon geometries."""
    if not scores:
        return gpd.GeoDataFrame()
        
    df = pd.DataFrame(scores)
    
    def hex_to_poly(hex_id):
        coords = get_hex_boundary(hex_id)
        # Shapely requires (lng, lat)
        return Polygon([(lng, lat) for lat, lng in coords])
        
    df['geometry'] = df['hex_id'].apply(hex_to_poly)
    
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.set_crs(epsg=4326, inplace=True)
    return gdf
