import streamlit as st
import random
import altair as alt
import pandas as pd

def render_metrics_row(cols):
    city = st.session_state.get("selected_city_name", "Chennai")
    selected_hex = st.session_state.get("selected_hex")
    
    if selected_hex:
        random.seed(hash(selected_hex))
    else:
        random.seed(hash(city))
        
    noise_val = round(random.uniform(55.0, 95.0), 1)
    transit_val = round(random.uniform(2.0, 45.0), 1)
    crowd_val = int(random.uniform(50, 800))
    heat_val = round(random.uniform(26.0, 44.0), 1)
    access_val = int(random.uniform(0, 12))
    
    # Generate explicit CSI Score matching map boundaries
    csi_score = round(max(0.0, min(1.0, random.gauss(0.4, 0.2))), 2)
    random.seed()
    
    with cols[0]:
        st.metric(label="🚥 Transit Delay", value=f"{transit_val} min/trip")
    with cols[1]:
        st.metric(label="🔊 Noise Level", value=f"{noise_val} dB")
    with cols[2]:
        st.metric(label="🌡️ Surface Heat", value=f"{heat_val} °C")
    with cols[3]:
        st.metric(label="🚶 Crowd Density", value=f"{crowd_val} ppl/km²")
    with cols[4]:
        st.metric(label="🚧 Incidents", value=f"{access_val}")
    with cols[5]:
        st.metric(label="📊 CSI Score", value=f"{csi_score}")

def render_csi_distribution():
    city = st.session_state.get("selected_city_name", "Chennai")
    
    csi_classes = ["Very Low", "Low", "Moderate", "High", "Critical"]
    random.seed(hash(city))
    dist = [random.randint(5, 40) for _ in range(5)]
    total = sum(dist)
    dist_pct = [round((x/total)*100, 1) for x in dist]
    
    colors = ['#4ade80', '#a3e635', '#facc15', '#f97316', '#ef4444']
    
    df_pie = pd.DataFrame({
        "Category": csi_classes,
        "Percentage": dist_pct,
        "Color": colors
    })
    
    chart = alt.Chart(df_pie).mark_arc(innerRadius=45).encode(
        theta=alt.Theta(field="Percentage", type="quantitative"),
        color=alt.Color(
            field="Category", 
            type="nominal", 
            scale=alt.Scale(domain=csi_classes, range=colors), 
            legend=alt.Legend(
                title=None, 
                orient="bottom", 
                columns=2,
                labelFontSize=13,
                symbolSize=100
            )
        ),
        tooltip=['Category', 'Percentage']
    ).properties(height=320)
    
    st.altair_chart(chart, use_container_width=True)
    random.seed()

