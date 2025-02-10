import os
import subprocess
from moviepy.editor import TextClip, VideoClip
from .text_renderer import create_text_ex, blur_text_clip
from typing import List, Tuple, Dict, Any, Callable
import logging
from functools import lru_cache
import pkg_resources

logger = logging.getLogger('shortcap.utils')

shadow_cache = {}
lines_cache = {}

def ffmpeg(command: List[str]) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e.stderr}")
        raise RuntimeError(f"FFmpeg command failed: {e.stderr}")

def get_font_path(font: str) -> str:
    """Get the full path to a font file."""
    if os.path.exists(font):
        return font
        
    # 如果是系统字体名称，直接返回
    if font in ["Arial", "Helvetica"]:
        return font
        
    raise FileNotFoundError(f"Font not found: {font}")

def detect_local_whisper(print_info: bool) -> bool:
    try:
        import whisper
        use_local_whisper = True
        if print_info:
            logger.info("Using local whisper model...")
    except ImportError:
        use_local_whisper = False
        if print_info:
            logger.info("Using OpenAI Whisper API...")

    return use_local_whisper

def fits_frame(line_count: int, font: str, font_size: int, stroke_width: int, text_bbox_width: int) -> Callable[[str], bool]:
    def fit_function(text):
        lines = calculate_lines(
            text,
            font,
            font_size,
            stroke_width,
            text_bbox_width
        )
        return len(lines["lines"]) <= line_count
    return fit_function

@lru_cache(maxsize=1024)
def calculate_lines(text: str, font: str, font_size: int, stroke_width: int, text_bbox_width: int) -> Dict[str, Any]:
    lines = []

    line_to_draw = None
    line = ""
    words = text.split()
    word_index = 0
    total_height = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size_ex(line.strip(), font, font_size, stroke_width)
        text_width = text_size[0]
        line_height = text_size[1]

        if text_width < text_bbox_width:
            line_to_draw = {
                "text": line.strip(),
                "height": line_height,
            }
            word_index += 1
        else:
            if not line_to_draw:
                logger.warning(f"Word '{line.strip()}' is too long for the frame!")
                line_to_draw = {
                    "text": line.strip(),
                    "height": line_height,
                }
                word_index += 1

            lines.append(line_to_draw)
            total_height += line_height
            line_to_draw = None
            line = ""

    if line_to_draw:
        lines.append(line_to_draw)
        total_height += line_height

    return {
        "lines": lines,
        "height": total_height,
    }

@lru_cache(maxsize=1024)
def create_shadow(text: str, font_size: int, font: str, blur_radius: float, opacity: float = 1.0) -> VideoClip:
    shadow = create_text_ex(text, font_size, "black", font, opacity=opacity)
    shadow = blur_text_clip(shadow, int(font_size*blur_radius))
    return shadow

@lru_cache(maxsize=1024)
def get_text_size_ex(text: str, font: str, fontsize: int, stroke_width: int) -> Tuple[int, int]:
    text_clip = create_text_ex(text, fontsize=fontsize, color="white", font=font, stroke_width=stroke_width)
    return text_clip.size
