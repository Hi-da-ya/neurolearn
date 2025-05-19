import streamlit as st
import requests
import os
from PIL import Image

# Config
BACKEND_URL = "http://localhost:5555/upload"
PROFILES = {
    "autistic": "Structured Steps",
    "dyslexic": "Phonetic Simplification", 
    "adhd": "Interactive Learning"
}

# Session State
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'content' not in st.session_state:
    st.session_state.content = None

# UI
st.set_page_config(page_title="NeuroLearn", layout="wide")
st.title("🧠 NeuroLearn")
st.write("### AI-Powered Learning for Neurodivergent Minds")

# Profile Selection
if not st.session_state.profile:
    st.write("## Get Started")
    profile = st.radio("Select your learning profile:", list(PROFILES.keys()))
    if st.button("Start Learning"):
        st.session_state.profile = profile
        st.rerun()

# Main App
else:
    st.write(f"**Profile:** {PROFILES[st.session_state.profile]}")
    
    uploaded_file = st.file_uploader("Upload notes (PDF/TXT/DOCX)", 
                                 type=["pdf", "txt", "docx"])    
    
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Original Content**")
            if uploaded_file.type != "text/plain":
                st.warning("File preview available for TXT only")
            else:
                st.text(uploaded_file.getvalue().decode())
        
        with col2:
            if st.button("✨ Adapt Content"):
                with st.spinner("Customizing..."):
                    files = {"file": uploaded_file}
                    data = {"profile": st.session_state.profile}
                    response = requests.post(BACKEND_URL, files=files, data=data)
                    
                    if response.status_code == 200:
                        st.session_state.content = response.json()["content"]
                        st.success("Content adapted successfully!")
                    else:
                        st.error(f"Error: {response.json().get('error')}")
        
        if st.session_state.content:
            st.divider()
            st.write("## Your Adapted Content")
            st.markdown(st.session_state.content)
            
            # Certificate Generation
            if st.button("🎓 Generate Certificate"):
                cert = Image.open("assets/certificate.png")
                st.image(cert, caption=f"NeuroLearn Achievement - {uploaded_file.name}")
                st.balloons()

    if st.button("← Change Profile"):
        st.session_state.profile = None
        st.rerun()