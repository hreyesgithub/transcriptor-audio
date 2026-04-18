import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import io

st.set_page_config(page_title="Transcriptor Audio en Vivo", page_icon="🎙️")
st.title("🎙️ Transcriptor de Audio en Vivo a Texto")

def transcribir_audio(archivo_subido):
    try:
        # 1. Cargar el audio completo desde el archivo subido
        # Es necesario pasar el archivo a AudioSegment primero
        # Se requiere FFmpeg instalado para formatos como MP3/M4A
        audio_completo = AudioSegment.from_file(archivo_subido)
        duracion_ms = len(audio_completo)
        segmento_ms = 20000  # 20 segundos
        
        reconocedor = sr.Recognizer()
        texto_acumulado = ""

        # 2. Elementos de la interfaz
        barra_progreso = st.progress(0)
        estado_texto = st.empty() 
        info_proceso = st.empty() 
        
        pasos = range(0, duracion_ms, segmento_ms)
        total_pasos = len(pasos)

        # 3. Bucle de procesamiento por fragmentos
        for i, inicio in enumerate(pasos):
            fin = min(inicio + segmento_ms, duracion_ms)
            
            # CORRECCIÓN: Recortamos el objeto 'audio_completo', NO el 'archivo_subido'
            chunk = audio_completo[inicio:fin]
            
            # Convertir fragmento a WAV en memoria
            buffer_wav = io.BytesIO()
            chunk.export(buffer_wav, format="wav")
            buffer_wav.seek(0)
            
            # Actualizar barra y estado
            porcentaje = int(((i + 1) / total_pasos) * 100)
            barra_progreso.progress(porcentaje)
            info_proceso.caption(f"Procesando: {inicio//1000}s - {fin//1000}s de {duracion_ms//1000}s")
            
            # Transcribir fragmento
            with sr.AudioFile(buffer_wav) as fuente:
                audio_data = reconocedor.record(fuente)
                try:
                    texto_fragmento = reconocedor.recognize_google(audio_data, language="es-ES")
                    texto_acumulado += texto_fragmento + " "
                    
                    # Actualizar el área de texto en tiempo real
                    estado_texto.text_area("Texto transcrito hasta el momento:", 
                                        value=texto_acumulado, 
                                        height=300)
                except sr.UnknownValueError:
                    continue 
                except Exception as e:
                    st.error(f"Error en segmento: {e}")

        return texto_acumulado

    except Exception as e:
        st.error(f"Error crítico: {e}")
        return None

# Interfaz de usuario
formatos_permitidos = ["ogg", "mp3", "wav", "m4a", "flac", "wma"]
archivo = st.file_uploader("Sube tu audio con los formatos permitidos", type=formatos_permitidos)

if archivo is not None:
    st.audio(archivo, format="audio/ogg")
    
    if st.button("Transcribir ahora"):
        resultado = transcribir_audio(archivo)
        
        if resultado:
            st.success("✅ ¡Transcripción completada!")
            st.download_button(
                label="Descargar transcripción (.txt)",
                data=resultado,
                file_name="transcripcion.txt",
                mime="text/plain"
            )
st.info("Nota: Esta aplicación requiere FFmpeg instalado en el sistema para manejar archivos OGG.")