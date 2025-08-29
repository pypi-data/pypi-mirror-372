from gtts import gTTS
import tempfile
import os
from playsound import playsound

class TTS:
    def __init__(self, lang="en"):
        self.lang = lang

    def play(self, text: str):
        """
        Play TTS audio on the local system speakers.
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=text, lang=self.lang)
            tts.save(fp.name)
            filename = fp.name

        try:
            playsound(filename)
        finally:
            try:
                os.remove(filename)
            except OSError:
                pass

    def save(self, text: str) -> str:
        """
        Generate TTS audio and return the filename of a temporary MP3 file.
        Useful for playing in Discord voice channels.
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=text, lang=self.lang)
            tts.save(fp.name)
            return fp.name
