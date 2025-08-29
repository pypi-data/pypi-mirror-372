# Python TTS  

A simple Python module for Text-to-Speech using the [gTTS](https://pypi.org/project/gTTS/) library.  

## Prerequisites  

- Python 3.9+  
- [gTTS](https://pypi.org/project/gTTS/) library  
- An audio player:  
  - **Windows** → Uses default media player  
  - **macOS** → Uses `afplay`  
  - **Linux** → Requires `mpg123` (`sudo apt install mpg123`)  

## Setup  

You can clone the repo and install dependencies in one go:  

```bash
git clone https://github.com/Madhav703/ease-tts.git
cd ease-tts
pip install -r requirements.txt
```

Or install directly from PyPI:  

```bash
pip install ease-tts
```

## Usage  

```python
from ease_tts import TTS

m = TTS()
m.play("Hello World")
```

This will generate speech and play **Hello World** on your system.  

### Notes for Discord usage:
- Requires **FFmpeg** installed and in system PATH (`ffmpeg -version` to check).  
- Make sure the bot has **Connect** and **Speak** permissions in the voice channel.  
- Temporary files are deleted after playback.  

## Notes  

- Requires an active internet connection (gTTS sends text to Google Translate TTS).  
- On Linux, ensure `mpg123` is installed for playback (system usage).  
- For Discord usage, ensure you have **FFmpeg** installed and available in PATH.  
- Temporary files are automatically cleaned up after playback.  

## Troubleshooting  

- `gtts.tts.gTTSError` → check your internet connection.  
- `FileNotFoundError: [Errno 2] No such file or directory: 'mpg123'` → install `mpg123` on Linux.  
- `ffmpeg not found` → install FFmpeg for Discord voice support.  
- Audio not playing on Windows (system usage) → check if your system has a default MP3 player set.  

## Contributing  

- Fork this repository and make your changes.  
- Test the module to ensure everything works.  
- Submit a pull request with a clear description.  

## License  

- This project is licensed under the MIT License – see the LICENSE file for details.  

## Facing any Issues?  

- You can open an issue on the [GitHub](https://github.com/Madhav703/ease-tts/issues) repo.  
