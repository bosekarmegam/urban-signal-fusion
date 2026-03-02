import streamlit as st
from dashboard.utils.theme import apply_ios_glass_theme

st.set_page_config(page_title="Urban Signal Fusion", layout="wide")
apply_ios_glass_theme()

from dashboard.components.hex_map import render_hex_map
from dashboard.components.alert_feed import render_alert_feed
from dashboard.components.signal_breakdown import render_metrics_row, render_csi_distribution

from dashboard.utils import location_api

st.title("Multi-Modal City Stress Score Engine")
st.markdown("Monitor high-frequency geospatial urban signals synthesized into a real-time **City Stress Index (CSI)** down to the street level.")

# Sidebar for Dynamic Location Selection
st.sidebar.header("🌍 Region Settings")

countries = location_api.get_countries()
selected_country = st.sidebar.selectbox("Select Country", countries, index=countries.index("India") if "India" in countries else 0)

states = location_api.get_states(selected_country) if selected_country else []
default_state_index = states.index("Tamil Nadu") if "Tamil Nadu" in states else 0
selected_state = st.sidebar.selectbox("Select State/Province", states, index=default_state_index)

cities = location_api.get_cities(selected_country, selected_state) if selected_state else []
default_city_index = cities.index("Chennai") if "Chennai" in cities else 0
selected_city = st.sidebar.selectbox("Select City", cities, index=default_city_index)

# Update Session State explicitly
if selected_city and selected_state and selected_country:
    st.session_state["selected_city_name"] = selected_city
    st.session_state["selected_state_name"] = selected_state
    st.session_state["selected_country_name"] = selected_country
    coords = location_api.get_coordinates(selected_city, selected_state, selected_country)
    st.session_state["city_lat"] = coords[0]
    st.session_state["city_lng"] = coords[1]
else:
    # Safe defaults
    st.session_state["selected_city_name"] = "Chennai"
    st.session_state["selected_state_name"] = "Tamil Nadu"
    st.session_state["selected_country_name"] = "India"
    st.session_state["city_lat"] = 13.0827
    st.session_state["city_lng"] = 80.2707

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Visual Settings")
st.session_state["hex_opacity"] = st.sidebar.slider("Hexagon Opacity", 0.1, 1.0, 0.6)

if st.session_state.get("selected_hex"):
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Active Selection")
    st.sidebar.code(st.session_state["selected_hex"])
    if st.sidebar.button("Clear Selection"):
        del st.session_state["selected_hex"]
        st.rerun()

from datetime import datetime
now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

st.sidebar.markdown("---")
st.sidebar.markdown(f"**🟢 Live Data Feed**<br><span style='color: #666; font-size: 0.9em; font-weight: 500;'>{now_str}</span>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Sync Live Data"):
    st.rerun()

st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align: center; color: #888; font-size: 0.8em;'>Built by <b>Suneel Bose K</b></div>", unsafe_allow_html=True)

# Layout
if st.session_state.get("selected_hex"):
    st.markdown(f"**Focusing on Sector:** `{st.session_state['selected_hex']}`")
else:
    st.markdown(f"**Focusing on City Avg:** `{selected_city}`")

m_cols = st.columns(6)
render_metrics_row(m_cols)
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 2])

with col1:
    render_hex_map()

with col2:
    st.markdown("##### 📍 Active Alerts")
    render_alert_feed()
    
    st.markdown("##### 📊 CSI Distribution")
    render_csi_distribution()
