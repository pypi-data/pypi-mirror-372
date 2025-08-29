# Configuration for the YouTube Subtitle Pipeline

# Whisper model options: tiny, base, small, medium, large
# Larger models are more accurate but slower
WHISPER_MODEL = "base"

# Output directory for processed videos
OUTPUT_DIR = "processed_videos"

# Temporary directory for intermediate files
TEMP_DIR = "temp"

# Netflix-style subtitle configuration
NETFLIX_SUBTITLE_STYLE = {
    "fontname": "Arial",
    "fontsize": 22,
    "bold": True,
    "primary_colour": "&H00FFFF00",    # Yellow text (BGR format)
    "secondary_colour": "&H00FFFF00",  
    "outline_colour": "&H00000000",    # Black outline
    "back_colour": "&H80000000",       # Semi-transparent black background
    "border_style": 3,                 # Background box style
    "outline": 2,                      # Thick outline
    "shadow": 0,                       # No shadow
    "alignment": 2,                    # Bottom center alignment
    "margin_left": 60,                 # Left margin
    "margin_right": 60,                # Right margin  
    "margin_vertical": 60              # Bottom margin
}

# Alternative subtitle styling options
SUBTITLE_STYLE = {
    "fontsize": 16,
    "primary_colour": "&Hffffff",  # White text
    "outline_colour": "&H000000",  # Black outline
    "back_colour": "&H80000000"    # Semi-transparent background
}

# Video quality settings
VIDEO_FORMAT = "best[ext=mp4]"  # Prefer MP4 format
AUDIO_FORMAT = "bestaudio"      # Best audio quality for transcription

# Processing options
MAX_RETRIES = 3                 # Number of retries for failed downloads
CLEANUP_TEMP_FILES = True       # Clean up temporary files after processing
