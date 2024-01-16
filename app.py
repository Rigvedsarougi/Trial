import os
import re
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import pandas as pd
import streamlit as st
import tempfile
from audio_processing import process_audio_chunk, process_audio_file, analyze_text_for_personal_details, detect_keywords

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
            'Job guarantee',
            '100% placement guarantee',
            'Personal account',
            'Refund',
            'S4 Hana',
            'Server Access',
            'Free classes',
            'Lifetime Membership',
            'Providing classes in token amount',
            'Pay later',
            'Global',
            'Abusive words',
            'Sarcastic',
            'Rude',
            'Darling in ILX',
            'Freelancing support we are provided',
            'Placement support we are provided',
            'Affirm',
            'Free classes we are not provided',
            'Free Days',
            'Free trial',
            'Trial classes',
            '+ 45 Days Trial Classes'
        ]

        results = process_audio_files(audio_files, keywords)
        result_df = pd.DataFrame(results)
        st.write(result_df)

if __name__ == "__main__":
    main()
