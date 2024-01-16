import logging
from functools import partial
import speech_recognition as sr
from pydub import AudioSegment

logging.basicConfig(level=logging.DEBUG)

def process_audio_chunk(chunk, recognizer):
    try:
        chunk.export("temp.wav", format="wav")
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, show_all=True, language='en-US')  # Adjust parameters
            if 'alternative' in text:
                text = text['alternative'][0]['transcript']
            return text
    except Exception as e:
        logging.error(f"Error processing audio chunk: {e}")
        return ""

def process_audio_file(audio_file, keywords):
    recognizer = sr.Recognizer()

    # Save BytesIO to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_file.write(audio_file.read())

    # Load temporary file with pydub
    audio = AudioSegment.from_mp3(temp_audio_file.name)

    chunk_size_ms = 5000
    chunks = [audio[i:i + chunk_size_ms] for i in range(0, len(audio), chunk_size_ms)]

    transcription = ""
    unrecognized_chunks_count = 0

    with sr.Pool() as pool:
        results = pool.map(partial(process_audio_chunk, recognizer=recognizer), chunks)

    for i, text in enumerate(results):
        if text:
            transcription += text + " "
        else:
            unrecognized_chunks_count += 1

    emails, phones, personal_account_detected = analyze_text_for_personal_details(transcription)

    keyword_results = detect_keywords(transcription, keywords)

    total_chunks = len(chunks)
    percentage_unrecognized = (unrecognized_chunks_count / total_chunks) * 100 if total_chunks > 0 else 0

    result = {
        'File Name': audio_file.name,
        'Fraud Detection': 'Fraud detected' if any(keyword_results.values()) else 'Not fraud detected',
        'Percentage Unrecognized': percentage_unrecognized,
        **keyword_results,
        'Personal Account Detection': 'Personal account detected' if personal_account_detected else 'Personal account not detected',
        'Personal Details': {'Emails': emails, 'Phones': phones}
    }

    return result

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
