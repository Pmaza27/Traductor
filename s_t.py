import os
import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import CustomJS, Button
from PIL import Image
from gtts import gTTS
from googletrans import Translator
import time
import glob

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Traductor de voz", page_icon="🎤", layout="centered")
st.title("🎙️ Traductor de Voz Multilingüe")
st.markdown("Habla, traduce y escucha tu voz en otro idioma.")

# --- IMAGEN / LOGO ---
if os.path.exists("OIG7.jpg"):
    image = Image.open("OIG7.jpg")
    st.image(image, width=250)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuración del traductor")
    st.info(
        "Presiona el botón principal para hablar. Luego selecciona el idioma de entrada, "
        "salida y acento para generar el audio traducido."
    )

# --- CREAR CARPETA TEMPORAL ---
os.makedirs("temp", exist_ok=True)

# --- BOTÓN DE ESCUCHA ---
st.subheader("Toca el botón y habla lo que quieras traducir:")
stt_button = Button(label="🎤 Escuchar", width=300, button_type="success")

stt_button.js_on_event(
    "button_click",
    CustomJS(
        code="""
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
    """
    ),
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

# --- ACCENTOS DISPONIBLES ---
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

# --- PROCESAR RESULTADO ---
if result and "GET_TEXT" in result:
    text = result["GET_TEXT"]
    st.success(f"🗣️ Texto detectado: {text}")

    translator = Translator()

    # Selección de lenguajes
    in_lang = st.selectbox("Idioma de entrada:", list(LANGUAGES.keys()), index=1)
    out_lang = st.selectbox("Idioma de salida:", list(LANGUAGES.keys()), index=0)
    accent = st.selectbox("Acento (solo para inglés):", list(ACCENTS.keys()), index=0)
    show_text = st.checkbox("Mostrar texto traducido", value=True)

    if st.button("🔊 Traducir y reproducir"):
        try:
            src_lang = LANGUAGES[in_lang]
            dest_lang = LANGUAGES[out_lang]
            tld = ACCENTS[accent]

            # Traducción
            translation = translator.translate(text, src=src_lang, dest=dest_lang)
            translated_text = translation.text

            # Síntesis de voz
            filename = f"temp/audio_{int(time.time())}.mp3"
            tts = gTTS(translated_text, lang=dest_lang, tld=tld, slow=False)
            tts.save(filename)

            st.audio(filename, format="audio/mp3")
            if show_text:
                st.markdown("### 📝 Traducción:")
                st.write(translated_text)

        except Exception as e:
            st.error(f"Ocurrió un error al traducir o generar audio: {e}")

# --- LIMPIAR ARCHIVOS ANTIGUOS ---
def remove_old_files(days=7):
    now = time.time()
    cutoff = now - days * 86400
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < cutoff:
            os.remove(f)

remove_old_files()
