import os
import re
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import pandas as pd
import streamlit as st
import tempfile
import logging
from pydub import AudioSegment
import speech_recognition as sr
from audio_processing import process_audio_chunk

logging.basicConfig(level=logging.DEBUG)

def analyze_text_for_personal_details(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    phone_pattern = re.compile(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b')
    personal_account_pattern = re.compile(r'\b(?:personal account)\b', re.IGNORECASE)

    emails_found = re.findall(email_pattern, text)
    phones_found = re.findall(phone_pattern, text)
    personal_account_detected = bool(re.search(personal_account_pattern, text))

    return emails_found, phones_found, personal_account_detected

def detect_keywords(input_text, keywords):
    keyword_presence = {keyword: bool(re.search(re.escape(keyword), input_text, re.IGNORECASE)) for keyword in keywords}
    return keyword_presence

def process_audio_file(audio_file, keywords):
    recognizer = sr.Recognizer()
    chunks = []

    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_file.write(audio_file.read())

    audio = AudioSegment.from_mp3(temp_audio_file.name)

    chunk_size_ms = 1000
    chunks = [audio[i:i + chunk_size_ms] for i in range(0, len(audio), chunk_size_ms)]

    transcription = ""
    unrecognized_chunks_count = 0

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(partial(process_audio_chunk, recognizer=recognizer), chunks))

    for i, text in enumerate(results):
        if text:
            transcription += text + " "
        else:
            unrecognized_chunks_count += 1

    temp_audio_file.close()

    del audio
    del results

    emails, phones, personal_account_detected = analyze_text_for_personal_details(transcription)

    keyword_results = detect_keywords(transcription, keywords)

    total_chunks = len(chunks)
    percentage_unrecognized = (unrecognized_chunks_count / total_chunks) * 100 if total_chunks > 0 else 0

    result = {
        'File Name': audio_file.name,
        'Transcription': transcription,
        'Fraud Detection': 'Fraud detected' if any(keyword_results.values()) else 'Not fraud detected',
        **keyword_results,
        'Personal Account Detection': 'Personal account detected' if personal_account_detected else 'Personal account not detected',
        'Personal Details': {'Emails': emails, 'Phones': phones}
    }

    return result

def process_audio_files(audio_files, keywords):
    results = []

    for audio_file in audio_files:
        result = process_audio_file(audio_file, keywords)
        results.append(result)

    return results

def main():
    st.title("Audio Fraud Detection")

    audio_files = st.file_uploader("Upload MP3 audio files", type=["mp3"], accept_multiple_files=True)

    if audio_files:
        keywords = [
            'Global',
            'HANA',
            'Server',
            'Software'
        ]

        results_list = []

        for audio_file in audio_files:
            result = process_audio_file(audio_file, keywords)
            results_list.append(result)  # Append the result to the list

            del result
            del audio_file

        results_df = pd.DataFrame(results_list)

        st.write(results_df)

        csv_data = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results CSV",
            data=csv_data,
            file_name="audio_fraud_detection_results.csv",
            key="download_button"
        )

        del results_df

if __name__ == "__main__":
    main()
