import streamlit as st
from PyPDF2 import PdfReader
import docx
from gtts import gTTS
import tempfile
import os
import sys
from PIL import Image

checkpoint_path = "Wav2Lip/checkpoints/wav2lip_gan.pth"
gdrive_url = f"https://drive.google.com/uc?id=1Jz_xnBmD7aD3hZAFQz73NTwxZU9fTuRi"
os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

st.set_page_config(page_title="WELCOME TO MY AVATAR", layout="wide")
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("### 👤 Customize Your Avatar")
page = st.sidebar.radio("", ["🏠Home Page", "🧠About", "📝Summary", "🚀Avatar"])
r = "#0B132B"
x = "#E0E0E0"
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {r};
            color: {x};
        }}
        .stTextInput > div > div > input {{
            background-color: #f0f0f0;
            color: #000000;
        }}
    </style>
    """,
    unsafe_allow_html=True
)
theme = st.sidebar.radio(
    "🎨 Choose Theme Mode:",
    ["🌙 Dark Mode", "🌞 Light Mode"],
    index=0
)
if theme == "🌞 Light Mode":
    st.markdown("""
        <style>
        .stApp {
            background-color: #DADADA;
            color: #000000;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #0B132B;
            color: #E0E0E0;
        }
        </style>
    """, unsafe_allow_html=True)
st.sidebar.markdown("### 🖋️ Font Settings")
font_size = st.sidebar.slider("🔠 Font Size", 12, 24, 16)

st.markdown(f"""
    <style>
    html, body, [class*="css"]  {{
        font-size: {font_size}px !important;
    }}
    .stMarkdown, .stText, .stTextInput, .stButton, .stRadio, .stSelectbox {{
        font-size: {font_size}px !important;
    }}
    </style>
""", unsafe_allow_html=True)
def extract_text_from_pdf(file):
    c = PyPDF2.PdfReader(file)
    text = ""
    for page in c.pages:
        text += page.extract_text()
    return text
def extract_text_from_docx(file):
    d = docx.Document(file)
    text = ""
    for para in d.paragraphs:
        text += para.text + '\n'
    return text
e = pipeline('summarization')
def summarize_text(text, max_length=150, min_length=50):
    summary = e(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
def text_to_speech(summary_text):
    f = gTTS(text=summary_text, lang='en')
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    f.save(temp_audio.name)
    return temp_audio.name
os.makedirs("../temp", exist_ok=True)
os.makedirs("../outputs", exist_ok=True)
if page == "🏠Home Page":
    st.title("🏠 Welcome to the Home Page")
    st.write("Welcome to your AI-powered avatar workspace — start creating, summarizing, and animating!.")
    st.markdown("""
       ### Features:
       - 📄 View summaries
       - 🧑‍💻 Customize your avatar
       - ℹ️ Learn more about this app
    """)
elif page == "🧠About":
    st.header("🧠About This App")
    st.subheader("📚content")
    st.write("This project builds an AI-powered talking avatar system that can generate human-like digital avatars, animate them with accurate lip-sync to speech, produce natural-sounding voice output, and even summarize text automatically before narration. It provides a seamless pipeline integrating avatar generation, speech synthesis, lip-sync animation, and text summarization, all accessible through an easy-to-use Streamlit web interface.")
    st.subheader("💡core features")
    st.write("1. Generates an avatar from an uploaded image (stylized or photorealistic).")
    st.write("2. Lip-Sync Animation (Wav2Lip): Precisely syncs the avatar’s mouth movements with the generated speech.")
    st.write("3. Speech Synthesis with gTTS: Convert text (or summarized text) into natural voice output.")
    st.write("4. Text Summarization: Automatically shortens long text inputs for smoother narration.")
    st.subheader("🌍 Applications")
    st.write("Education: Generate visual explainers and virtual tutors.")
    st.write("Marketing: Create digital brand ambassadors or talking ads.")
    st.write("Entertainment: Build AI storytellers or animated hosts.")
    st.write("Accessibility: Provide visual speech for inclusive content.")
elif page == "📝Summary":
    st.header("📝Summary View")
    st.write("Upload a document or enter text to generate a summary and listen to it.")
    g = st.radio("Choose Input Type:", ["Upload Document", "Enter Text"])
    raw_text = ""
    if g == "Upload Document":
        b = st.file_uploader('Upload a document or PDF', type=['pdf', 'docx'])
    elif g == "Enter Text":
        user_input = st.text_area("Enter text for summarization:", height=200)
        b = None
        raw_text = user_input
    if st.button('Generate Summary'):
        if g == "Upload Document" and b is None:
            st.warning("Please upload a valid document.")
            st.stop()
        elif g == "Enter Text" and not raw_text.strip():
            st.warning("Please enter text for summarization.")
            st.stop()
        if g == "Upload Document":
            if b.name.endswith(".pdf"):
                raw_text = extract_text_from_pdf(b)
            elif b.name.endswith(".docx"):
                raw_text = extract_text_from_docx(b)
            else:
                st.warning("Unsupported file type.")
                st.stop()
            h = summarize_text(raw_text)
        else:
            h = summarize_text(raw_text)
        st.subheader("Summary")
        st.write(h)
        audio_path = text_to_speech(h)
        st.audio(audio_path, format="audio/mp3")
elif page == "🚀Avatar":
    st.header("🚀Avatar Settings")
    g = st.radio("Choose Input Type:", ["Upload Document", "Enter Text"])
    a = st.file_uploader('Upload avatar image', type=['png', 'jpg'])
    raw_text = ""
    if g == "Upload Document":
        b = st.file_uploader('Upload a document or PDF', type=['pdf', 'docx'])
    elif g == "Enter Text":
        user_input = st.text_area("Enter text for your avatar to speak:", height=200)
        b = None
        raw_text = user_input
    if st.button('Generate Talking Avatar'):
        if a is None:
            st.warning("Please upload an avatar image.")
            st.stop()
        if g == "Upload Document" and b is None:
            st.warning("Please upload a valid document before generating.")
            st.stop()
        elif g == "Enter Text" and not raw_text.strip():
            st.warning("Please enter some text for your avatar to speak.")
            st.stop()
        avatar_path = "../outputs/avatar.png"
        with open(avatar_path, "wb") as f:
            f.write(a.read())
        if g == "Upload Document":
            if b.name.endswith(".pdf"):
                raw_text = extract_text_from_pdf(b)
            elif b.name.endswith(".docx"):
                raw_text = extract_text_from_docx(b)
            else:
                st.warning("Unsupported file type.")
                st.stop()
            h = summarize_text(raw_text)
            st.subheader("Summary")
            st.write(h)
            audio_input = h
        else:
            st.subheader("Your Text")
            st.write(raw_text)
            audio_input = raw_text
        audio_path = text_to_speech(audio_input)
        st.audio(audio_path, format="audio/mp3")
        j = subprocess.run([
            sys.executable, "Wav2Lip/inference.py",
            "--checkpoint_path", "Wav2Lip/checkpoints/wav2lip_gan.pth",
            "--face", avatar_path,
            "--audio", audio_path,
            "--outfile", "outputs/talking.mp4"
        ], shell=True, capture_output=True, text=True)
        outfile_path = "outputs/talking.mp4"

        if j.returncode == 0 and os.path.exists(outfile_path):
            st.header("Avatar")
            st.markdown("""
                <style>
                video {
                    max-height: 520px !important;   /* reduce video height */
                    width: auto !important;          /* keep aspect ratio */
                    border-radius: 12px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                }
                </style>
            """, unsafe_allow_html=True)
            st.video(outfile_path)
        else:
            st.error("Wav2Lip failed — see error logs below.")
            st.text(j.stderr)




















