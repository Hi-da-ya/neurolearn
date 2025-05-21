import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
from streamlit_extras.card import card
import textwrap
import io
import os

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
#Certificate generation
def generate_certificate(profile_name, file_name, profile_icon):
    # Create blank image (800x600 pixels)
    img = Image.new('RGB', (800, 600), color=(250, 245, 240))  # Cream background
    d = ImageDraw.Draw(img)
    
    # Colors based on profile
    profile_colors = {
        "autistic": (78, 121, 167),   # Muted blue
        "dyslexic": (89, 161, 79),    # Leaf green
        "adhd": (242, 142, 43)        # Vibrant orange
    }
    color = profile_colors.get(profile_name.lower(), (0, 0, 0))
    
    # Decorative border
    d.rectangle([(50, 50), (750, 550)], outline=color, width=4)
    d.rectangle([(60, 60), (740, 540)], outline=(200, 200, 200), width=2)
    
    try:
        # Try to load a Unicode-compatible font (Arial Unicode MS if available)
        try:
            title_font = ImageFont.truetype("arialuni.ttf", 36)  # Windows Unicode font
        except:
            try:
                title_font = ImageFont.truetype("DejaVuSans.ttf", 36)  # Linux fallback
            except:
                title_font = ImageFont.load_default()
        
        main_font = ImageFont.truetype("arial.ttf", 24) if os.path.exists("arial.ttf") else title_font
        small_font = ImageFont.truetype("arial.ttf", 18) if os.path.exists("arial.ttf") else title_font
    except:
        # Final fallback to default font
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header - Without Unicode characters first for sizing
    d.text((400, 100), "NEUROLEARN ACHIEVEMENT", fill=color, 
           font=title_font, anchor="mm")
    
    # Main text - Handle Unicode characters carefully
    content_lines = [
        "Certificate of Completion",
        "",
        f"This certifies that the learning material:",
        f'"{textwrap.fill(file_name, width=30)}"',
        "has been successfully adapted for",
        f"{profile_name} Learners",
        "",
        "Congratulations!"
    ]
    
    y_position = 250
    for line in content_lines:
        if profile_icon in line:  # Handle icon separately
            # Draw text before icon
            parts = line.split(profile_icon)
            if parts[0]:
                d.text((400, y_position), parts[0], fill=(50, 50, 50), 
                      font=main_font, anchor="mm")
                # Get width to position icon
                w = d.textlength(parts[0], font=main_font)
                d.text((400 + w//2 + 10, y_position-5), profile_icon, 
                      fill=color, font=main_font)
                if parts[1]:
                    d.text((400 + w//2 + 30, y_position), parts[1], 
                          fill=(50, 50, 50), font=main_font)
            else:
                d.text((400, y_position), profile_icon, fill=color, 
                      font=main_font, anchor="mm")
        else:
            d.text((400, y_position), line, fill=(50, 50, 50), 
                  font=main_font, anchor="mm")
        y_position += 40
    
    # Footer
    d.text((400, 500), "neurolearn.ai | Empowering Diverse Minds", 
           fill=(150, 150, 150), font=small_font, anchor="mm")
    
    return img
    # Create blank image (800x600 pixels)
    img = Image.new('RGB', (800, 600), color=(250, 245, 240))  # Cream background
    
    d = ImageDraw.Draw(img)
    
    # Colors based on profile
    profile_colors = {
        "autistic": (78, 121, 167),   # Muted blue
        "dyslexic": (89, 161, 79),    # Leaf green
        "adhd": (242, 142, 43)        # Vibrant orange
    }
    color = profile_colors.get(profile_name.lower(), (0, 0, 0))
    
    # Decorative border
    d.rectangle([(50, 50), (750, 550)], outline=color, width=4)
    d.rectangle([(60, 60), (740, 540)], outline=(200, 200, 200), width=2)
    
    try:
        # Try to load nice fonts (will fall back to default if not available)
        title_font = ImageFont.truetype("arialbd.ttf", 36)
        main_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    d.text((400, 100), "NEUROLEARN ACHIEVEMENT", fill=color, 
           font=title_font, anchor="mm")
    
    # Main text
    content = f"""\n\nCertificate of Completion\n\n
This certifies that the learning material:\n
"{textwrap.fill(file_name, width=30)}"\n
has been successfully adapted for\n
{profile_icon} {profile_name} Learners\n\n
Congratulations!"""
    
    d.multiline_text((400, 250), content, fill=(50, 50, 50), 
                    font=main_font, anchor="mm", align="center", spacing=15)
    
    # Footer
    d.text((400, 500), "neurolearn.ai | Empowering Diverse Minds", 
           fill=(150, 150, 150), font=small_font, anchor="mm")
    
    return img    

# Header
header_col1, header_col2 = st.columns([3,1])
with header_col1:
    st.title(f"{'🧠 NeuroLearn' if not st.session_state.profile else PROFILES[st.session_state.profile]['icon']}")
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
    st.caption(f"We'll adapt these for your {profile_data['approach_name']} profile")
    
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
        if st.button(f"✨ Adapt for {profile_data['approach_name']}", type="primary"):
            with st.spinner(f"Customizing for {profile_data['approach_name']}..."):
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
                profile_data['approach_name']
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
                # Generate the certificate
                cert = generate_certificate(
                    profile_data['display_name'].replace(" Learners", ""),
                    st.session_state.uploaded_file.name,
                    profile_data['icon']
                )
                
                # Display and offer download
                st.image(cert, caption="Your NeuroLearn Achievement Certificate")
                st.balloons()
                
                # Convert to bytes for download
                buf = io.BytesIO()
                cert.save(buf, format="PNG")
                
                st.download_button(
                    label="⬇️ Download Certificate",
                    data=buf.getvalue(),
                    file_name=f"neurolearn_certificate_{st.session_state.profile}.png",
                    mime="image/png",
                    help="Save your achievement certificate"
                )
                st.success("Certificate generated successfully!")
        # Feedback
        st.divider()
        with st.expander("💬 Provide Feedback on This Adaptation"):
            rating = st.slider("How helpful was this adaptation?", 1, 5, 3)
            comments = st.text_area("Additional comments")
            if st.button("Submit Feedback"):
                st.toast("Thank you for your feedback!", icon="🙏")