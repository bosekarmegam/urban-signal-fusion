import streamlit as st
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) UrbanSignalFusion/1.0'}
BASE_URL = "https://countriesnow.space/api/v0.1"

@st.cache_data(ttl=3600*24)
def get_countries():
    try:
        res = requests.get(f"{BASE_URL}/countries/iso", headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        return [item['name'] for item in data.get('data', [])]
    except Exception as e:
        st.error(f"Error fetching countries: {e}")
        return ["India", "United States", "United Kingdom", "Canada"]

@st.cache_data(ttl=3600*24)
def get_states(country):
    try:
        res = requests.post(f"{BASE_URL}/countries/states", json={"country": country}, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        return [item['name'] for item in data.get('data', {}).get('states', [])]
    except Exception as e:
        st.error(f"Error fetching states for {country}: {e}")
        return []

@st.cache_data(ttl=3600*24)
def get_cities(country, state):
    try:
        res = requests.post(f"{BASE_URL}/countries/state/cities", json={"country": country, "state": state}, headers=HEADERS, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data.get('data', [])
    except Exception as e:
        st.error(f"Error fetching cities for {state}, {country}: {e}")
        return []

@st.cache_data(ttl=3600*24)
def get_coordinates(city, state, country):
    geolocator = Nominatim(user_agent="urban_signal_fusion_dashboard")
    query = f"{city}, {state}, {country}"
    try:
        location = geolocator.geocode(query, timeout=10)
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        st.warning(f"Geocoding timed out for {query}.")
    except Exception as e:
        st.error(f"Geocoding error: {e}")
    # Fallback to Chennai if fails
    return 13.0827, 80.2707

@st.cache_data(ttl=3600*24)
def get_city_hexes(city, state, country, resolution=8):
    import h3
    import urllib.parse
    
    query = urllib.parse.quote(f"{city}, {state}, {country}")
    url = f"https://nominatim.openstreetmap.org/search.php?q={query}&polygon_geojson=1&format=jsonv2"
    
    try:
        req = requests.get(url, headers={'User-Agent': 'urban-signal-fusion-app'}, timeout=15)
        res_data = req.json()
        if res_data and len(res_data) > 0 and 'geojson' in res_data[0]:
            geojson = res_data[0]['geojson']
            geom_type = geojson.get("type", "")
            coords = geojson.get("coordinates", [])
            hexes = set()
            
            # Helper to convert [lng, lat] to (lat, lng) and polyfill
            def polyfill_ring(ring):
                # H3 expects (lat, lng)
                geo_ring = [(p[1], p[0]) for p in ring]
                # h3.polygon_to_cells takes h3.Polygon(exterior, *holes)
                poly = h3.Polygon(geo_ring)
                return h3.polygon_to_cells(poly, resolution)

            if geom_type == "Polygon":
                hexes.update(polyfill_ring(coords[0]))
            elif geom_type == "MultiPolygon":
                for poly_coords in coords:
                    hexes.update(polyfill_ring(poly_coords[0]))
                    
            if hexes:
                return list(hexes)
    except Exception as e:
        pass
        
    # Fallback to a disk around coordinates
    lat, lng = get_coordinates(city, state, country)
    center_hex = h3.latlng_to_cell(lat, lng, resolution)
    return list(h3.grid_disk(center_hex, 10))
