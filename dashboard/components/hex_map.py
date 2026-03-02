import streamlit as st
import pydeck as pdk
import pandas as pd
import random
import h3

def get_color(csi: float) -> list[int]:
    """Map 0-1 CSI to Green-Yellow-Red (Light-themed pastel aesthetic)."""
    if csi < 0.5:
        r = int((csi / 0.5) * 255)
        g = int(255 - (csi / 0.5) * 60)
        b = 60
    else:
        r = 255
        g = int((1.0 - ((csi - 0.5) / 0.5)) * 200)
        b = 60
    return [r, g, b]

def render_hex_map():
    from dashboard.utils import location_api
    city_name = st.session_state.get("selected_city_name", "Chennai")
    state_name = st.session_state.get("selected_state_name", "Tamil Nadu")
    country_name = st.session_state.get("selected_country_name", "India")
    lat = st.session_state.get("city_lat", 13.0827)
    lng = st.session_state.get("city_lng", 80.2707)
    
    # Generate geometric areas for TRUE city bounds at resolution 8
    data_hexes = set(location_api.get_city_hexes(city_name, state_name, country_name, resolution=8))
    
    # Background trap radius (spans huge area under map for unbounded click interception)
    center_hex = h3.latlng_to_cell(lat, lng, 8)
    bg_hexes = set(h3.grid_disk(center_hex, 40)) - data_hexes
    
    data = []
    for h in data_hexes:
        random.seed(hash(h))
        csi = max(0.0, min(1.0, random.gauss(0.4, 0.2)))
        noise_val = round(random.uniform(55.0, 95.0), 1)
        transit_val = round(random.uniform(2.0, 45.0), 1)
        crowd_val = int(random.uniform(50, 800))
        heat_val = round(random.uniform(26.0, 44.0), 1)
        access_val = int(random.uniform(0, 12))
        data.append({
            "hex": h, 
            "csi": round(csi, 2), 
            "color": get_color(csi),
            "type": "data",
            "noise": noise_val,
            "transit": transit_val,
            "crowd": crowd_val,
            "heat": heat_val,
            "alerts": access_val
        })
    random.seed()
        
    df_data = pd.DataFrame(data)
    
    # Build invisible trap layer
    bg_data = [{"hex": h, "type": "background"} for h in bg_hexes]
    df_bg = pd.DataFrame(bg_data)
    
    layer_data = pdk.Layer(
        "H3HexagonLayer",
        df_data,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        opacity=st.session_state.get("hex_opacity", 0.65),
        get_hexagon="hex",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 200],
        line_width_min_pixels=1,
    )
    
    layer_bg = pdk.Layer(
        "H3HexagonLayer",
        df_bg,
        pickable=True,
        stroked=False,
        filled=True,
        extruded=False,
        opacity=0.0, # Completely invisible
        get_hexagon="hex",
        get_fill_color=[0, 0, 0, 0],
    )
    
    import math
    if data_hexes:
        lats = [h3.cell_to_latlng(h)[0] for h in data_hexes]
        lngs = [h3.cell_to_latlng(h)[1] for h in data_hexes]
        lat_span = max(lats) - min(lats)
        lng_span = max(lngs) - min(lngs)
        max_span = max(lat_span, lng_span)
        
        # Calculate dynamic zoom to fit the city bounding box comfortably
        if max_span > 0:
            zoom_level = math.log2(180 / (max_span * 1.1)) # 2.5 is a padding factor
            zoom_level = max(3.0, min(14.0, zoom_level))
        else:
            zoom_level = 10.5
    else:
        zoom_level = 10.5
        
    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lng,
        zoom=zoom_level,
        bearing=0,
        pitch=25
    )
    
    tooltip = {
        "html": "<b>Hex:</b> {hex}<br/>"
                "<b>CSI Score:</b> {csi}<br/>"
                "<b>Transit:</b> {transit} min<br/>"
                "<b>Noise:</b> {noise} dB<br/>"
                "<b>Heat:</b> {heat} &deg;C<br/>"
                "<b>Crowd:</b> {crowd} ppl/km&sup2;<br/>"
                "<b>Incidents:</b> {alerts}",
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "color": "#333",
            "font-family": "Inter, sans-serif",
            "padding": "12px",
            "border-radius": "12px",
            "box-shadow": "0 8px 30px rgba(0,0,0,0.12)"
        }
    }
    
    # Stack the core data precisely on top of the invisible trap geometries
    r = pdk.Deck(
        layers=[layer_bg, layer_data], 
        initial_view_state=view_state, 
        tooltip=tooltip,
        map_style="light" # Requests CartoDB Positron format automatically
    )
    
    # Enable bidirectional selection with fixed height explicitly ensuring single-screen iOS aesthetic
    event = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object", height=500)
    
    if event and event.selection and event.selection.get("objects"):
        obj = event.selection["objects"][0]
        selected_hex = obj.get("hex")
        obj_type = obj.get("type")
        
        if obj_type == "background":
            # Map Panned Click Detected -> Recenter geographic arrays!
            new_lat, new_lng = h3.cell_to_latlng(selected_hex)
            st.session_state["city_lat"] = new_lat
            st.session_state["city_lng"] = new_lng
            st.session_state["selected_hex"] = None # Drop isolated focus
            st.rerun()
        else:
            if selected_hex and st.session_state.get("selected_hex") != selected_hex:
                st.session_state["selected_hex"] = selected_hex
                st.rerun()
    
