"""
voice.py — reconnaissance vocale (STT) et synthèse vocale (TTS).
STT : SpeechRecognition (Google Web API gratuit, hors-ligne possible via Whisper).
TTS : pyttsx3 (hors-ligne, voix Windows SAPI5).
"""

import speech_recognition as sr
import pyttsx3


# Initialisation unique du moteur TTS
_engine = pyttsx3.init()
_engine.setProperty("rate", 175)   # vitesse de parole


def speak(text: str):
    """Prononce le texte à voix haute."""
    print(f"[voice] Jarvis dit : {text}")
    _engine.say(text)
    _engine.runAndWait()


def listen_speech(timeout: int = 10) -> str | None:
    """
    Écoute le micro et retourne le texte reconnu, ou None si rien capté.
    timeout : durée max d'écoute en secondes.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        print("[voice] Écoute en cours...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language="fr-FR")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[voice] Erreur STT : {e}")
            return None
