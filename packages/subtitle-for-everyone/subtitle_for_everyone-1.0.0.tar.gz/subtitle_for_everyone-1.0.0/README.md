# SubPlz - Subtitle Pipeline for Everyone

🎬 **Automatically download YouTube videos and burn Netflix-style subtitles into them!**

[![PyPI version](https://badge.fury.io/py/subtitle-for-everyone.svg)](https://badge.fury.io/py/subtitle-for-everyone)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🚀 **One-command processing** - Just provide a YouTube URL or local video
- 🎯 **Netflix-style subtitles** - Professional yellow text with black background
- 🤖 **AI-powered transcription** - Uses OpenAI Whisper for accurate subtitles
- 🎥 **Multiple formats** - Supports YouTube URLs and local video files
- 🔧 **Smart dependency handling** - Guides you through installing missing dependencies
- 🧹 **Automatic cleanup** - Removes temporary files after processing

## 📦 Installation

```bash
pip install subtitle-for-everyone
```

## 📋 System Requirements

### Required Dependencies
- **Python 3.8+**
- **FFmpeg** - For video processing
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### Python Dependencies (Installed Automatically)
- `yt-dlp` - YouTube video downloading
- `openai-whisper` - AI subtitle generation
- `torch` - Machine learning backend
- `ffmpeg-python` - Video processing
- `tqdm` - Progress bars

## 🚀 Quick Start

### Process YouTube Videos

```bash
# Single YouTube video
subplz https://www.youtube.com/watch?v=VIDEO_ID

# The command will:
# 1. Download the video
# 2. Generate subtitles using AI
# 3. Burn Netflix-style subtitles into the video
# 4. Save to 'processed_videos' folder
```

### Process Local Videos

```bash
# Local video file
subplz /path/to/your/video.mp4
subplz "C:\\Users\\Name\\Videos\\myvideo.mp4"
```

### Custom Output Directory

```bash
subplz https://www.youtube.com/watch?v=VIDEO_ID -o my_output_folder
```

## 🎨 Netflix-Style Subtitles

SubPlz creates professional subtitles that look just like Netflix:

- **Yellow text** (#FFFF00) for visibility
- **Black background box** with semi-transparency  
- **Arial Bold font** at size 22
- **Bottom center positioning** with proper margins
- **Thick black outline** for readability on any background

## 📁 Output

- Processed videos are saved with `_with_subtitles` suffix
- Original video quality is preserved
- Subtitles are permanently burned into the video
- Temporary files are automatically cleaned up

## 🛠️ Dependency Troubleshooting

If you get dependency errors, SubPlz will guide you:

### Missing FFmpeg
```
❌ Missing dependencies: ffmpeg

📋 Installation Instructions:
🔸 To install FFmpeg:
   Windows: Download from https://ffmpeg.org/download.html
   macOS: brew install ffmpeg  
   Linux: sudo apt install ffmpeg
   Then add FFmpeg to your system PATH
```

### Missing yt-dlp
```
❌ Missing dependencies: yt-dlp

📋 Installation Instructions:  
🔸 To install yt-dlp:
   pip install yt-dlp
```

## 🔧 Advanced Configuration

SubPlz uses sensible defaults, but you can customize behavior by modifying the config:

```python
# In your Python code
from subplz.config import NETFLIX_SUBTITLE_STYLE

# Customize subtitle appearance
NETFLIX_SUBTITLE_STYLE['fontsize'] = 24  # Bigger text
NETFLIX_SUBTITLE_STYLE['primary_colour'] = "&Hffffff"  # White text
```

## 📖 Examples

### Basic Usage
```bash
# Download and add subtitles to a YouTube video
subplz "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Batch Processing Script
```python
import subprocess

urls = [
    "https://www.youtube.com/watch?v=VIDEO1",
    "https://www.youtube.com/watch?v=VIDEO2", 
    "https://www.youtube.com/watch?v=VIDEO3"
]

for url in urls:
    subprocess.run(["subplz", url])
```

### Local Video Processing
```bash
# Add subtitles to local videos
subplz "/Users/name/Movies/lecture.mp4"
subplz "C:\\Downloads\\presentation.mp4"  
```

## 🐛 Troubleshooting

### Common Issues

1. **"Command not found: subplz"**
   ```bash
   pip install --upgrade subtitle-for-everyone
   # Or try: python -m subplz
   ```

2. **"FFmpeg not found"**
   - Install FFmpeg and add to system PATH
   - Restart terminal after installation

3. **Out of memory errors**
   - Use smaller Whisper model: modify `WHISPER_MODEL = "tiny"` in config

4. **Video download failures**
   - Some videos may be region-blocked or private
   - Try different video URLs

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- **GitHub Issues**: [github.com/guider23/subplz/issues](https://github.com/guider23/subplz/issues)
- **Email**: sofiyasenthilkumar@gmail.com

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - AI transcription
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [FFmpeg](https://ffmpeg.org/) - Video processing

---

**Made with ❤️ by Sid & Kan**
