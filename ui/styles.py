import os
import base64
import streamlit as st

def get_base64_image(image_path):
    """Encodes an image to base64 so it can be safely injected into CSS as a background."""
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode()
                return f"data:image/jpeg;base64,{encoded}"
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
    return ""

def inject_custom_css(bg_image_type="img1"):
    """
    Injects CSS stylesheet rules directly into the Streamlit app.
    Loads Outfit and Inter typography and sets up glassmorphic styling and a premium dark gradient background.
    """
    # Load custom background image base64 if available
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if bg_image_type == "img1":
        bg_path = os.path.join(current_dir, "img5.jpeg")
    else:
        bg_path = os.path.join(current_dir, "img4.jpeg")
        
    bg_base64 = get_base64_image(bg_path)
    
    if bg_base64:
        # Use the base64-encoded image as the background with a premium dark gradient overlay for optimal text contrast
        background_css = f"""
        .stApp {{
            background: linear-gradient(rgba(11, 15, 20, 0.85), rgba(11, 15, 20, 0.85)), url("{bg_base64}") no-repeat center center fixed;
            background-size: cover;
        }}
        """
    else:
        # Sleek fallback premium dark gradient background
        background_css = """
        .stApp {
            background: linear-gradient(135deg, #090D10 0%, #121A21 50%, #070A10 100%);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        """
        
    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Core Typography & Variables */
    {background_css}
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }}
    
    /* Hide Streamlit Header, Footer, and Hamburger Menu */
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: #0F1419;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #202D3A;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #00D4FF;
    }}
    
    /* Gradient Title Text */
    .gradient-text {{
        background: linear-gradient(135deg, #00D4FF 0%, #00FF88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }}
    
    .gold-gradient-text {{
        background: linear-gradient(135deg, #FFB800 0%, #FF6B6B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }}
    
    /* Glassmorphic Executive Cards */
    .glass-card {{
        background: rgba(22, 29, 36, 0.75);
        backdrop-filter: blur(12px) saturate(120%);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        border: 1px solid rgba(0, 212, 255, 0.4);
        box-shadow: 0 8px 32px 0 rgba(0, 212, 255, 0.08);
        transform: translateY(-2px);
    }}
    
    /* Custom Streamlit Form Styling */
    div[data-testid="stForm"] {{
        background: rgba(22, 29, 36, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 184, 0, 0.15) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5) !important;
    }}
    
    /* Custom Streamlit Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #00D4FF 0%, #0088CC 100%) !important;
        color: #0F1419 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 10px 24px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5) !important;
        color: #0F1419 !important;
    }}
    
    .stButton>button:active {{
        transform: translateY(1px) !important;
    }}
    
    /* Custom Secondary Buttons (PDF, Replay, etc.) */
    div.secondary-btn .stButton>button {{
        background: rgba(22, 29, 36, 0.7) !important;
        color: #E0E0E0 !important;
        border: 1.5px solid rgba(0, 212, 255, 0.3) !important;
        box-shadow: none !important;
    }}
    
    /* Gold Accent Button Container */
    div.gold-btn .stButton>button {{
        background: linear-gradient(135deg, #FFB800 0%, #D48800 100%) !important;
        box-shadow: 0 4px 15px rgba(255, 184, 0, 0.3) !important;
        color: #0F1419 !important;
    }}
    
    div.gold-btn .stButton>button:hover {{
        box-shadow: 0 6px 20px rgba(255, 184, 0, 0.5) !important;
        color: #0F1419 !important;
    }}
    
    div.secondary-btn .stButton>button:hover {{
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1.5px solid #00D4FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(0, 212, 255, 0.15) !important;
    }}
    
    /* Form Inputs Overrides */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {{
        background-color: #0B0E12 !important;
        border: 1px solid #202D3A !important;
        border-radius: 10px !important;
    }}
    
    div[data-baseweb="select"] {{
        background-color: #0B0E12 !important;
        border: 1px solid #202D3A !important;
        border-radius: 10px !important;
    }}
    
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {{
        border: 1px solid #00D4FF !important;
    }}
    
    /* Slider Custom Styling */
    div[role="slider"] {{
        background-color: #00D4FF !important;
    }}
    
    /* Boardroom Meeting Status Indicators */
    .status-badge {{
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }}
    
    .status-thinking {{
        background: rgba(255, 184, 0, 0.15);
        color: #FFB800;
        border: 1px solid rgba(255, 184, 0, 0.3);
        animation: pulse-orange 1.5s infinite ease-in-out;
    }}
    
    .status-speaking {{
        background: rgba(0, 212, 255, 0.15);
        color: #00D4FF;
        border: 1px solid rgba(0, 212, 255, 0.3);
        animation: pulse-blue 1.2s infinite ease-in-out;
    }}
    
    .status-completed {{
        background: rgba(0, 255, 136, 0.15);
        color: #00FF88;
        border: 1px solid rgba(0, 255, 136, 0.3);
    }}
    
    /* Chat bubbles for boardroom debate */
    .chat-bubble {{
        padding: 16px 20px;
        border-radius: 14px;
        margin-bottom: 15px;
        background: rgba(22, 29, 36, 0.5);
        border-left: 4px solid #E0E0E0;
        backdrop-filter: blur(5px);
    }}
    
    /* Metric Ring styling */
    .metric-container {{
        text-align: center;
        padding: 15px;
        background: rgba(22, 29, 36, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
    }}
    
    .metric-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #00D4FF;
        margin: 5px 0;
    }}
    
    .metric-label {{
        font-size: 12px;
        color: #9E9E9E;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    
    /* Keyframe Animations */
    @keyframes pulse-orange {{
        0% {{ transform: scale(1); opacity: 0.9; }}
        50% {{ transform: scale(1.02); opacity: 1; }}
        100% {{ transform: scale(1); opacity: 0.9; }}
    }}
    
    @keyframes pulse-blue {{
        0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 212, 255, 0.4); }}
        70% {{ transform: scale(1.01); box-shadow: 0 0 0 6px rgba(0, 212, 255, 0); }}
        100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 212, 255, 0); }}
    }}
    
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
