import os
import re
import numpy as np
import librosa
import speech_recognition as sr
from pydub import AudioSegment
from transformers import pipeline

# -------------------------
# Load Sentiment Pipelines
# -------------------------
try:
    # Multilingual star-rating sentiment model
    star_pipeline = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )

    # RoBERTa-based sentiment classification (positive, neutral, negative)
    roberta_pipeline = pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment",
        return_all_scores=True
    )

except Exception as e:
    raise RuntimeError(f"Failed to load sentiment models: {str(e)}")


# -------------------------
# Audio Transcription
# -------------------------
def transcribe_audio(audio_path: str) -> str:
    """
    Converts an audio file into text using Google Speech Recognition.
    Supports multiple audio formats by converting everything to WAV.
    """
    temp_wav = None
    try:
        # Convert to WAV if needed
        if not audio_path.endswith(".wav"):
            temp_wav = f"{audio_path}.wav"
            AudioSegment.from_file(audio_path).export(temp_wav, format="wav")
            audio_path = temp_wav

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        return recognizer.recognize_google(audio)

    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Speech recognition service unavailable"
    except Exception as e:
        return f"Audio transcription error: {str(e)}"
    finally:
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)


# -------------------------
# Sentiment Analysis
# -------------------------
def analyze_sentiment(text: str) -> dict:
    """
    Performs sentiment analysis using two models:
    - Multilingual star-rating classification (1-5 stars)
    - RoBERTa-based positive/neutral/negative scoring
    """
    try:
        # Get star-rating sentiment
        star_result = star_pipeline(text)[0]
        star_value = int(star_result["label"].split()[0])

        # Get detailed sentiment distribution from RoBERTa
        roberta_results = roberta_pipeline(text)[0]
        sentiment_scores = {
            "negative": next(r["score"] for r in roberta_results if r["label"] == "LABEL_0"),
            "neutral": next(r["score"] for r in roberta_results if r["label"] == "LABEL_1"),
            "positive": next(r["score"] for r in roberta_results if r["label"] == "LABEL_2")
        }

        return {
            "star_rating": star_value,
            "star_score": star_result["score"],
            "sentiment_scores": sentiment_scores
        }
    except Exception as e:
        raise RuntimeError(f"Sentiment analysis failed: {str(e)}")


# -------------------------
# Pitch Analysis
# -------------------------
def analyze_pitch(audio_path: str) -> float:
    """
    Analyzes the average pitch frequency (Hz) of the audio.
    Returns 0 if pitch detection fails.
    """
    try:
        y, sr = librosa.load(audio_path, sr=None)
        pitches = librosa.yin(y, fmin=80, fmax=400)
        valid_pitches = pitches[~np.isnan(pitches)]

        return float(np.mean(valid_pitches)) if len(valid_pitches) > 0 else 0.0
    except Exception as e:
        print(f"Pitch analysis warning: {str(e)}")
        return 0.0


# -------------------------
# Extract Call Schedule
# -------------------------
def extract_call_schedule(text: str):
    """
    Extracts scheduled call times from text using multiple patterns.
    Returns a list of times if found, otherwise None.
    """
    patterns = [
        r'(?:call you|we\'ll call|call back|schedule).*?(?:at|on)?\s?(\d{1,2}:\d{2}\s?(?:AM|PM)?|\d{1,2}\s?(?:AM|PM))',
        r'(?:next call|follow-up|follow up).*?(?:at|on)?\s?(\d{1,2}:\d{2}\s?(?:AM|PM)?|\d{1,2}\s?(?:AM|PM))',
        r'(?:scheduled for|set for|planned for)\s?(\d{1,2}:\d{2}\s?(?:AM|PM)?|\d{1,2}\s?(?:AM|PM))',
        r'(?:tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s?(\d{1,2}:\d{2}\s?(?:AM|PM)?|\d{1,2}\s?(?:AM|PM))'
    ]

    found_times = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.group(1):
                found_times.append(match.group(1).upper())

    return list(set(found_times)) if found_times else None


# -------------------------
# Main Audio Analysis
# -------------------------
def analyze_audio_file(audio_path: str) -> dict:
    """
    Performs full analysis:
    1. Transcribe audio → text
    2. Sentiment analysis on text
    3. Pitch detection
    4. Extract possible scheduled call times
    """
    try:
        transcription = transcribe_audio(audio_path)
        sentiment = analyze_sentiment(transcription)
        avg_pitch = analyze_pitch(audio_path)
        scheduled_times = extract_call_schedule(transcription)

        return {
            "success": True,
            "transcription": transcription,
            "star_rating": sentiment["star_rating"],
            "star_score": sentiment["star_score"],
            "sentiment_scores": sentiment["sentiment_scores"],
            "average_pitch": avg_pitch,
            "scheduled_times": scheduled_times
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
