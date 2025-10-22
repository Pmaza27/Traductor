import os
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import CustomJS, Button
from gtts import gTTS
from googletrans import Translator
import time
import glob
from PIL import Image

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Traductor de Voz", page_icon="🎧", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #232526 0%, #414345 100%);
    color: #f8f9fa;
    font-family: 'Poppins', sans-serif;
}
h1, h2, h3 {
    text-align: center;
    color: #ffffff;
}
[data-testid="stAppViewContainer"] > .main {
    background: rgba(255, 255, 255, 0.07);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.5);
    backdrop-filter: blur(12px);
}
.stButton > button {
    background-color: #00ADB5;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    font-size: 1.1rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: #08d9d6;
    transform: scale(1.03);
}
.stAudio {
    border-radius: 10px;
}
.stSelectbox, .stCheckbox, .stTextInput {
    color: black;
}
.sidebar .sidebar-content {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title("🎙️ Traductor de Voz Multilingüe")
st.markdown("Convierte tu voz en otro idioma y escúchala al instante 🌍")

# --- IMAGEN / LOGO ---
if os.path.exists("OIG7.jpg"):
    st.image("OIG7.jpg", width=200)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.write("Presiona el botón principal para hablar, luego selecciona los idiomas y el acento que prefieras.")

# --- CARPETA TEMPORAL ---
os.makedirs("temp", exist_ok=True)

# --- BOTÓN DE ESCUCHA ---
st.markdown("### 🔻 Pulsa para hablar:")
stt_button = Button(label="🎤 Escuchar", width=300, button_type="success")

stt_button.js_on_event(
    "button_click",
    CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES';
        recognition.onresult = function (e) {
            var value = e.results[0][0].transcript;
            if (value) {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
    """),
)

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
)

# --- MAPA DE IDIOMAS ---
LANGUAGES = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de",
    "Italiano": "it",
    "Portugués": "pt",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
    "Coreano": "ko",
    "Bengalí": "bn",
}

ACCENTS = {
    "Defecto": "com",
    "México": "com.mx",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canadá": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
}

translator = Translator()

# --- RESULTADO DE VOZ ---
if result and "GET_TEXT" in result:
    text = result["GET_TEXT"]
    st.success(f"🗣️ Detectado: *{text}*")

    col1, col2 = st.columns(2)
    with col1:
        in_lang = st.selectbox("Idioma de entrada:", list(LANGUAGES.keys()), index=1)
    with col2:
        out_lang = st.selectbox("Idioma de salida:", list(LANGUAGES.keys()), index=0)

    accent = st.selectbox("Acento (solo para inglés):", list(ACCENTS.keys()), index=0)
    show_text = st.checkbox("Mostrar texto traducido", value=True)

    st.divider()

    if st.button("🔊 Traducir y reproducir"):
        try:
            src_lang = LANGUAGES[in_lang]
            dest_lang = LANGUAGES[out_lang]
            tld = ACCENTS[accent]

            translation = translator.translate(text, src=src_lang, dest=dest_lang)
            translated_text = translation.text

            filename = f"temp/audio_{int(time.time())}.mp3"
            tts = gTTS(translated_text, lang=dest_lang, tld=tld, slow=False)
            tts.save(filename)

            st.audio(filename, format="audio/mp3")

            if show_text:
                st.markdown("### 📝 Traducción:")
                st.markdown(f"<div style='font-size:1.2rem;color:#00FFF5;'>{translated_text}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# --- LIMPIEZA ---
def remove_old_files(days=3):
    now = time.time()
    cutoff = now - days * 86400
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)
remove_old_files()
