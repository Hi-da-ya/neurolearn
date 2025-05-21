import streamlit as st
import requests
from PIL import Image
from streamlit_extras.card import card

# Config
BACKEND_URL = "http://localhost:5555/upload"
PROFILES = {
    "autistic": {
        "display_name": "Autistic Learners",
        "approach_name": "Structured Steps",
        "icon": "🧩",
        "description": "Clear, predictable learning paths with visual structure",
        "features": [
            "Visual schedules",
            "Step-by-step breakdowns",
            "Consistent formatting",
            "Reduced sensory overload"
        ]
    },
    "dyslexic": {
        "display_name": "Dyslexic Learners",
        "approach_name": "Phonetic Simplification", 
        "icon": "🔤",
        "description": "Text adaptation with phonetic support and readability focus",
        "features": [
            "Dyslexia-friendly fonts",
            "Phonetic spellings",
            "Enhanced spacing",
            "Multi-sensory options"
        ]
    },
    "adhd": {
        "display_name": "ADHD Learners",
        "approach_name": "Interactive Learning",
        "icon": "⚡",
        "description": "Engaging, dynamic content with frequent interaction points",
        "features": [
            "Chunked information",
            "Interactive elements",
            "Focus timers",
            "Gamification"
        ]
    }
}
# Session State
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'content' not in st.session_state:
    st.session_state.content = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# UI
st.set_page_config(page_title="NeuroLearn", layout="wide", page_icon="🧠")

# Custom CSS
st.markdown("""
<style>
    .profile-card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .profile-card:hover {
        border-color: #4a8af4;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .selected-card {
        border: 2px solid #4a8af4 !important;
        background-color: #f8faff;
    }
    .progress-bar {
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        margin: 10px 0;
    }
    .progress {
        height: 100%;
        border-radius: 4px;
        background-color: #4a8af4;
    }
    .file-info {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
header_col1, header_col2 = st.columns([3,1])
with header_col1:
    st.title(f"{'🧠 NeuroLearn' if not st.session_state.profile else PROFILES[st.session_state.profile]['icon']} NeuroLearn")
    st.write("AI-Powered Learning for Neurodivergent Minds")
with header_col2:
    if st.session_state.profile:
        if st.button("← Change Profile", use_container_width=True):
            st.session_state.profile = None
            st.session_state.content = None
            st.session_state.uploaded_file = None
            st.rerun()

# Profile Selection
if not st.session_state.profile:
    st.subheader("Choose Your Learning Profile")
    st.write("Select the approach that best fits your learning style:")
    
    cols = st.columns(3)
    for i, (profile_key, profile_data) in enumerate(PROFILES.items()):
        with cols[i]:
            clicked = card(
                title=f"{profile_data['icon']} {profile_data['display_name']}",
                text=profile_data['description'],
                key=f"card_{profile_key}"
            )
            if clicked or st.button(f"Select {profile_data['display_name']}", key=f"btn_{profile_key}"):
                st.session_state.profile = profile_key
                st.rerun()

# Main App
else:
    profile_data = PROFILES[st.session_state.profile]
    
    # Progress tracker
    st.markdown("""
    <div class="progress-bar">
        <div class="progress" style="width: {}%"></div>
    </div>
    """.format(25 if st.session_state.uploaded_file else 0 if not st.session_state.content else 50 if st.session_state.content else 75), 
    unsafe_allow_html=True)
    
    # File Upload Section
    st.subheader("Step 1: Upload Your Learning Materials")
    st.caption(f"We'll adapt these for your {profile_data['name']} profile")
    
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload notes (PDF/TXT/DOCX)", 
        type=["pdf", "txt", "docx"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        
        with st.expander("File Details"):
            st.write(f"**Type:** {uploaded_file.type}")
            st.write(f"**Size:** {len(uploaded_file.getvalue()) / 1000:.1f} KB")
            
            if uploaded_file.type == "text/plain":
                st.divider()
                st.text_area("File Preview", 
                           uploaded_file.getvalue().decode(),
                           height=200)
    
    # Content Adaptation
    if st.session_state.uploaded_file and not st.session_state.content:
        st.subheader("Step 2: Adapt Content")
        if st.button(f"✨ Adapt for {profile_data['name']}", type="primary"):
            with st.spinner(f"Customizing for {profile_data['name']}..."):
                files = {"file": st.session_state.uploaded_file}
                data = {"profile": st.session_state.profile}
                response = requests.post(BACKEND_URL, files=files, data=data)
                
                if response.status_code == 200:
                    st.session_state.content = response.json()["content"]
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
    
    # Display Adapted Content
    if st.session_state.content:
        st.subheader("Step 3: Your Adapted Content")
        st.markdown("""<div class="file-info">
            <b>Original File:</b> {} • <b>Adaptation Profile:</b> {}
            </div>""".format(
                st.session_state.uploaded_file.name,
                profile_data['name']
            ), unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Formatted View", "Raw Text"])
        
        with tab1:
            st.markdown(st.session_state.content)
        
        with tab2:
            st.code(st.session_state.content)
        
        # Learning Tools
        st.divider()
        st.subheader("Learning Tools")
        
        tool_cols = st.columns(3)
        
        with tool_cols[0]:
            if st.button("📝 Create Quiz", help="Generate practice questions from this content"):
                st.info("Quiz generation coming soon!")
        
        with tool_cols[1]:
            if st.button("🔊 Audio Version", help="Listen to the adapted content"):
                st.info("Audio conversion coming soon!")
        
        with tool_cols[2]:
            if st.button("🎓 Generate Certificate", type="primary"):
                cert = Image.open("assets/certificate.png")
                st.image(cert, caption=f"NeuroLearn Achievement - {st.session_state.uploaded_file.name}")
                st.balloons()
                st.success("Certificate generated! Download available soon.")
        
        # Feedback
        st.divider()
        with st.expander("💬 Provide Feedback on This Adaptation"):
            rating = st.slider("How helpful was this adaptation?", 1, 5, 3)
            comments = st.text_area("Additional comments")
            if st.button("Submit Feedback"):
                st.toast("Thank you for your feedback!", icon="🙏")