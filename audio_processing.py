import logging
import speech_recognition as sr
from pydub import AudioSegment

logging.basicConfig(level=logging.DEBUG)

def process_audio_chunk(chunk, recognizer):
    try:
        # Export the audio chunk to a temporary WAV file
        chunk.export("temp.wav", format="wav")

        # Recognize the audio using Google Speech Recognition
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
        
        # Use a more robust recognition method to handle all alternatives
        text = ""
        try:
            # Use the Google Web Speech API to get all alternatives
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
