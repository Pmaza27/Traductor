import os
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import CustomJS, Button
from gtts import gTTS
from googletrans import Translator
import time
import glob
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Traductor de Voz", page_icon="🎧", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

body {
    background-color: #f9f4ec; /* Fondo crema */
    color: #2b2b2b;
    font-family: 'Poppins', sans-serif;
}

/* Contenedor principal */
[data-testid="stAppViewContainer"] > .main {
    background: #ffffffcc;
    border-radius: 25px;
    padding: 3rem 2rem;
    box-shadow: 0px 8px 30px rgba(0,0,0,0.1);
    max-width: 750px;
    margin: 2rem auto;
}

/* Títulos */
h1 {
    text-align: center;
    color: #1a1a1a;
    font-weight: 700;
    font-size: 2.6rem;
    letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
}
h2, h3 {
    color: #333333;
    font-weight: 600;
    text-align: center;
}

/* Subtexto */
p, .stMarkdown {
    font-size: 1rem;
    color: #444;
}

/* Botones */
.stButton > button {
    display: block;
    margin: 0 auto;
    background-color: #3b82f6; /* azul suave */
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.9rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(59,130,246,0.4);
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    background-color: #2563eb;
    transform: scale(1.05);
}

/* Selects y checkboxes */
.stSelectbox, .stCheckbox {
    color: #1a1a1a;
}

/* Audio player */
.stAudio {
    border-radius: 12px;
}

/* Sidebar */
.sidebar .sidebar-content {
    background: #fffaf3;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title("🎙️ Traductor de Voz")
st.markdown(
    "<p style='text-align:center; font-size:1.1rem; color:#555;'>Habla, traduce y escucha tu voz en otro idioma al instante 🌍</p>",
    unsafe_allow_html=True,
)

# --- IMAGEN / LOGO ---
if os.path.exists("Diversity.jpeg"):
    st.image("Diversuty.jpeg", width=180)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Presiona el botón principal para hablar y luego selecciona el idioma y el acento que prefieras.")

# --- CARPETA TEMPORAL ---
os.makedirs("temp", exist_ok=True)

# --- BOTÓN DE ESCUCHA ---
st.markdown("<h3 style='text-align:center;'>🎤 Pulsa para hablar:</h3>", unsafe_allow_html=True)
stt_button = Button(label="Escuchar ahora", width=350, button_type="success")

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

    accent = st.selectbox("Acento (solo inglés):", list(ACCENTS.keys()), index=0)
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
                st.markdown(
                    f"<div style='font-size:1.2rem; color:#2563eb; text-align:center; margin-top:1rem;'>📝 {translated_text}</div>",
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

# --- LIMPIEZA DE AUDIOS ANTIGUOS ---
def remove_old_files(days=3):
    now = time.time()
    cutoff = now - days * 86400
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)
remove_old_files()
