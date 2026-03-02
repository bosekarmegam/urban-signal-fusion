import streamlit as st

def apply_ios_glass_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* App Background */
        .stApp {
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            background-attachment: fixed;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Prevent scrolling & Hide Header/Footer */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        footer {display: none !important;}
        
        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.4) !important;
            backdrop-filter: blur(25px) saturate(150%);
            -webkit-backdrop-filter: blur(25px) saturate(150%);
            border-right: 1px solid rgba(255, 255, 255, 0.6);
        }
        
        /* Metrics Cards Glassmorphism */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.65) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            border-radius: 20px !important;
            padding: 8px 15px !important;
            box-shadow: 0 10px 40px rgba(31, 38, 135, 0.05) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 50px rgba(31, 38, 135, 0.1) !important;
        }
        
        /* Prevent Metric Truncation */
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
            line-height: 1.2 !important;
            white-space: pre-wrap !important;
            overflow: visible !important;
        }
        [data-testid="stMetricValue"] > div {
            overflow: visible !important;
            white-space: pre-wrap !important;
            text-overflow: clip !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            margin-bottom: 2px !important;
            white-space: nowrap !important;
            overflow: visible !important;
        }
        
        /* Typography adjustments */
        h1, h2, h3, h4 {
            color: #1c1c1e !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
        }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.15rem !important; margin-bottom: 0.5rem !important; }
        
        p, span, label {
            color: #3a3a3c !important;
        }
        
        /* Map Container styling */
        .stDeckGlJsonChart {
            border-radius: 24px !important;
            overflow: visible !important;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1) !important;
            border: 4px solid rgba(255, 255, 255, 0.7) !important;
            height: 50vh !important;
        }
        
        /* Buttons */
        button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 14px !important;
            color: #007aff !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04) !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 1.0) !important;
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(0,122,255,0.15) !important;
        }
        
        /* Inputs & Selectboxes */
        .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTimeInput input {
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.02) !important;
            font-weight: 500 !important;
        }
        </style>
    """, unsafe_allow_html=True)
