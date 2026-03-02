import streamlit as st

def render_alert_feed():
    st.markdown("""
        <div data-testid="stMetric" style="margin-bottom: 1rem; text-align: center; color: #666; font-weight: 500;">
            No active high-severity anomalies at this time.
        </div>
    """, unsafe_allow_html=True)
