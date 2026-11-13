import streamlit as st
import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
LOGO_PATH = r"C:\Users\Udarsh\.gemini\antigravity\brain\32e4c94e-9dbf-4ddc-8742-a7fd61464518\setu_logo_1785409259763.jpg"

st.set_page_config(page_title="Setu", page_icon="🌾", layout="centered")

# --- Custom Black & Purple Aesthetic CSS ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except:
        return ""

st.markdown(f"""
<style>
/* Main Background: Black and Deep Purple Gradient */
.stApp {{
    background: linear-gradient(135deg, #000000 0%, #11001c 50%, #1a0b2e 100%) !important;
    background-attachment: fixed;
    color: #e0e0e0;
    font-size: 1.15rem; /* Zoom in a bit globally */
}}

/* Hide main menu and footer for clean look */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Typography */
h1, h2, h3, h4, h5, h6, p, span, div, label {{
    font-family: 'Inter', 'Roboto', sans-serif !important;
}}
h1 {{
    background: -webkit-linear-gradient(45deg, #d387ff, #8224e3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}}
h3 {{
    color: #d387ff !important;
    font-weight: 400 !important;
    margin-top: -10px !important;
}}

/* Glassmorphism Containers */
div[data-baseweb="input"] > div, 
div[data-baseweb="select"] > div,
.stTextArea textarea, 
.stFileUploader, 
.stTabs [data-baseweb="tab-list"],
.stExpander,
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(20, 10, 30, 0.5) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(130, 36, 227, 0.3) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
    color: white !important;
}}

/* Clean Inputs */
input {{
    color: #ffffff !important;
    font-size: 1.15rem !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(90deg, #510e94 0%, #8224e3 100%) !important;
    border: 1px solid rgba(211, 135, 255, 0.2) !important;
    border-radius: 25px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    font-size: 1.15rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(130, 36, 227, 0.3) !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(130, 36, 227, 0.6) !important;
    border: 1px solid rgba(211, 135, 255, 0.5) !important;
}}

/* Success/Error/Warning Messages */
.stSuccess, .stError, .stWarning, .stInfo {{
    background: rgba(30, 15, 45, 0.8) !important;
    backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(211, 135, 255, 0.2) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    color: #e0e0e0 !important;
    font-size: 1.15rem !important;
}}

/* Tab Styling */
button[data-baseweb="tab"] {{
    color: #a0a0a0 !important;
    font-size: 1.15rem !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: #ffffff !important;
}}

/* Top header structural padding */
.css-18e3th9 {{
    padding-top: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# --- Header & Logo perfectly aligned using Flexbox ---
img_base64 = get_base64_image(LOGO_PATH)
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 30px; margin-bottom: 30px; margin-top: 15px;">
    <img src="data:image/jpeg;base64,{img_base64}" width="120" style="border-radius: 20px; box-shadow: 0 4px 15px rgba(130, 36, 227, 0.4);">
    <div>
        <h1 style="margin: 0; padding: 0; font-size: 4rem; line-height: 1;">Setu</h1>
        <h3 style="margin: 0; padding: 0; font-size: 1.6rem; color: #d387ff; font-weight: 400; margin-top: 5px !important;">Next-Gen Offline Farm Advisory</h3>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Configuration ---
with st.expander("⚙️ Advanced Configuration"):
    language_override = st.selectbox(
        "Language Override:", 
        ["Auto-detect", "English", "Tamil", "Telugu", "Hindi"],
        help="Force a specific language if auto-detection fails."
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Interface ---
tab1, tab2 = st.tabs(["💬 Chat", "📸 Visual & Audio"])

with tab1:
    with st.container(border=True):
        st.markdown("### Ask a Question")
        user_query = st.text_input("Enter your query (English, Tamil, Telugu, Hindi, or Code-switched):", placeholder="e.g. How to treat late blight in potatoes?", label_visibility="collapsed")
        
        col_btn, _ = st.columns([3, 7])
        with col_btn:
            ask_btn = st.button("Ask Assistant", use_container_width=True)
            
        if ask_btn:
            if user_query:
                with st.spinner("Analyzing..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/chat", 
                            data={"text": user_query, "language_override": language_override}, timeout=30
                        )
                        if response.status_code == 200:
                            st.success("Response Generated:")
                            st.write(response.json().get("response", "No response returned."))
                        else:
                            st.error(f"Error connecting to backend: {response.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend API: {e}")
            else:
                st.warning("Please enter a query.")

with tab2:
    with st.container(border=True):
        st.markdown("### Multimodal Input")
        st.info("Take a photo of a crop or pest, or upload an audio question.")
        
        camera_image = st.camera_input("Take a picture")
        
        image_file = st.file_uploader("Or upload leaf/crop image", type=["jpg", "jpeg", "png"])
        st.markdown("*Note: Use `.wav` for optimal offline processing.*")
        audio_file = st.file_uploader("Upload audio recording", type=["wav", "mp3", "m4a"])
        
        final_image = camera_image if camera_image else image_file
        
        col_btn2, _ = st.columns([4, 6])
        with col_btn2:
            process_btn = st.button("Process Multimodal Input", use_container_width=True)
            
        if process_btn:
            if audio_file or final_image:
                with st.spinner("Processing Media..."):
                    files = {}
                    data = {"language_override": language_override}
                    if audio_file:
                        files["audio"] = (audio_file.name, audio_file.getvalue(), audio_file.type)
                    if final_image:
                        files["image"] = (final_image.name, final_image.getvalue(), final_image.type)
                        
                    try:
                        response = requests.post(f"{BACKEND_URL}/chat", data=data, files=files)
                        if response.status_code == 200:
                            st.success("Analysis Complete:")
                            st.write(response.json().get("response", "No response returned."))
                        else:
                            st.error(f"Error connecting to backend: {response.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend API: {e}")
            else:
                st.warning("Please provide a photo or audio file.")

# --- Footer ---
st.markdown("""
<div style="text-align: center; margin-top: 60px; padding: 20px; color: #a0a0a0; font-family: 'Inter', sans-serif; font-size: 1.1rem; border-top: 1px solid rgba(130, 36, 227, 0.2);">
    Developed by team <b>CodeKnight</b>
</div>
""", unsafe_allow_html=True)
