from fastapi import APIRouter, HTTPException, Query
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from cachetools import cached, TTLCache
import h3
import urllib.parse
from typing import List

router = APIRouter(tags=["locations"])

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) UrbanSignalFusion/1.0'}
BASE_URL = "https://countriesnow.space/api/v0.1"

# In-memory caches to replace Streamlit's @st.cache_data
cache = TTLCache(maxsize=100, ttl=86400)

@router.get("/locations/countries", response_model=List[str])
@cached(cache)
def get_countries():
    try:
        res = requests.get(f"{BASE_URL}/countries/iso", headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        return [item['name'] for item in data.get('data', [])]
    except Exception as e:
        return ["India", "United States", "United Kingdom", "Canada"]

@router.get("/locations/states", response_model=List[str])
def get_states(country: str):
    cache_key = f"states_{country}"
    if cache_key in cache:
        return cache[cache_key]
    try:
        res = requests.post(f"{BASE_URL}/countries/states", json={"country": country}, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        states = [item['name'] for item in data.get('data', {}).get('states', [])]
        cache[cache_key] = states
        return states
    except Exception as e:
        return []

@router.get("/locations/cities", response_model=List[str])
def get_cities(country: str, state: str):
    cache_key = f"cities_{country}_{state}"
    if cache_key in cache:
        return cache[cache_key]
    try:
        res = requests.post(f"{BASE_URL}/countries/state/cities", json={"country": country, "state": state}, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        cities = data.get('data', [])
        cache[cache_key] = cities
        return cities
    except Exception as e:
        return []

def get_coordinates(city, state, country):
    geolocator = Nominatim(user_agent="urban_signal_fusion_dashboard_react")
    query = f"{city}, {state}, {country}"
    try:
        location = geolocator.geocode(query, timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

@router.get("/locations/hexes")
def get_city_hexes(
    city: str = Query(...), 
    state: str = Query(...), 
    country: str = Query(...), 
    resolution: int = Query(8)
):
    cache_key = f"hexes_{city}_{state}_{country}_{resolution}"
    if cache_key in cache:
        return cache[cache_key]
        
    query = urllib.parse.quote(f"{city}, {state}, {country}")
    url = f"https://nominatim.openstreetmap.org/search.php?q={query}&polygon_geojson=1&format=jsonv2&limit=1"
    
    hexes = set()
    center_lat, center_lng = None, None
    
    try:
        req = requests.get(url, headers={'User-Agent': 'urban-signal-fusion-app-react'}, timeout=15)
        res_data = req.json()
        if res_data and len(res_data) > 0:
            if 'lat' in res_data[0] and 'lon' in res_data[0]:
                center_lat = float(res_data[0]['lat'])
                center_lng = float(res_data[0]['lon'])
                
            if 'geojson' in res_data[0]:
                geojson = res_data[0]['geojson']
                geom_type = geojson.get("type", "")
                coords = geojson.get("coordinates", [])
                
                # Helper to convert [lng, lat] to (lat, lng) and polyfill
                def polyfill_ring(ring):
                    geo_ring = [(p[1], p[0]) for p in ring]
                    poly = h3.Polygon(geo_ring)
                    return h3.polygon_to_cells(poly, resolution)

                if geom_type == "Polygon":
                    hexes.update(polyfill_ring(coords[0]))
                elif geom_type == "MultiPolygon":
                    for poly_coords in coords:
                        hexes.update(polyfill_ring(poly_coords[0]))
    except Exception as e:
        pass
        
    if not center_lat or not center_lng:
        center_lat, center_lng = get_coordinates(city, state, country)
        
    if not center_lat or not center_lng:
        return {"hexes": [], "center": None}
        
    if not hexes:
        # Fallback to a disk around coordinates
        center_hex = h3.latlng_to_cell(center_lat, center_lng, resolution)
        hexes = set(h3.grid_disk(center_hex, 10))
        
    result = {
        "hexes": list(hexes),
        "center": [center_lat, center_lng]
    }
    cache[cache_key] = result
    return result
