import logging
import speech_recognition as sr
from pydub import AudioSegment

logging.basicConfig(level=logging.DEBUG)

def process_audio_chunk(chunk, recognizer):
    try:
        chunk.export("temp.wav", format="wav")

        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
        
        text = ""
        try:
            response = recognizer.recognize_google(audio_data, show_all=True, language='en-US')
            
            if 'alternative' in response:
                alternatives = response['alternative']
                transcripts = [alt['transcript'] for alt in alternatives]
                text = " ".join(transcripts)
        except Exception as e:
            logging.error(f"Error recognizing alternatives: {e}")

        return text
    except Exception as e:
        logging.error(f"Error processing audio chunk: {e}")
        return ""
