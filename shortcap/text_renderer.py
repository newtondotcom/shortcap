from moviepy.editor import TextClip, ImageClip, VideoClip, CompositeVideoClip
from PIL import Image, ImageFilter, ImageFont
import numpy
import tempfile
from typing import List, Union, Optional, Tuple
import logging
import os
import pkg_resources

logger = logging.getLogger('shortcap.text_renderer')

text_cache = {}

class TextRenderer:
    def __init__(self, font_path=None, font_size=40, font_color="white", stroke_width=0, stroke_color="black"):
        if font_path is None:
            # 使用默认字体
            font_path = pkg_resources.resource_filename('shortcap', 'assets/fonts/TitanOne-Regular.ttf')
        
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found at {font_path}")
            
        self.font_path = font_path
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

class Character:
    def __init__(self, text: str, color: Optional[str] = None):
        self.text: str = text
        self.color: Optional[str] = color

    def set_color(self, color: str) -> None:
        self.color = color

class Word:
    def __init__(self, word: str, color: Optional[str] = None):
        self.word: str = word
        self.color: Optional[str] = color
        self.characters: List[Character] = []

        for char in word:
            self.characters.append(Character(char, color))

    def set_color(self, color: str) -> None:
        self.color = color
        for char in self.characters:
            char.set_color(color)

class TextClipEx(TextClip):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text: str = kwargs["txt"]

def moviepy_to_pillow(clip: VideoClip) -> Image.Image:
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".png").name
        clip.save_frame(temp_file)
        image = Image.open(temp_file)
        return image
    except Exception as e:
        logger.error(f"Failed to convert MoviePy clip to Pillow image: {str(e)}")
        raise RuntimeError(f"Failed to convert MoviePy clip to Pillow image: {str(e)}")

def get_text_size(text: str, fontsize: int, font: str, stroke_width: int) -> Tuple[int, int]:
    text_clip = create_text(text, fontsize=fontsize, color="white", font=font, stroke_width=stroke_width)
    return text_clip.size

def get_text_size_ex(text: str, font: str, fontsize: int, stroke_width: int) -> Tuple[int, int]:
    text_clip = create_text_ex(text, fontsize=fontsize, color="white", font=font, stroke_width=stroke_width)
    return text_clip.size

def blur_text_clip(text_clip: VideoClip, blur_radius: int) -> VideoClip:
    # Convert TextClip to a PIL image
    pil_img = moviepy_to_pillow(text_clip)

    # Offset blur to make it centered
    offset = int(blur_radius * 0.6)

    # Add empty space around text for blur
    pil_img_padded = Image.new("RGBA", (pil_img.width + blur_radius * 3, pil_img.height + blur_radius * 3))
    pil_img_padded.paste(moviepy_to_pillow(text_clip), (blur_radius+offset, blur_radius+offset))

    # Create a blurred version of the text
    pil_img_padded = pil_img_padded.filter(
        ImageFilter.GaussianBlur(radius=blur_radius)
    )

    text_clip = ImageClip(numpy.array(pil_img_padded))
    text_clip = text_clip.set_duration(text_clip.duration)

    return text_clip

def create_text(
    text: str,
    fontsize: int,
    color: str,
    font: str,
    bg_color: str = 'transparent',
    blur_radius: int = 0,
    opacity: float = 1.0,
    stroke_color: Optional[str] = None,
    stroke_width: int = 1,
    kerning: float = 0.0,
) -> VideoClip:
    global text_cache

    arg_hash = hash((text, fontsize, color, font, bg_color, blur_radius, opacity, stroke_color, stroke_width, kerning))

    if arg_hash in text_cache:
        return text_cache[arg_hash].copy()

    text_clip = TextClipEx(txt=text, fontsize=fontsize, color=color, bg_color=bg_color, font=font, stroke_color=stroke_color, stroke_width=stroke_width, kerning=kerning)

    text_clip = text_clip.set_opacity(opacity)

    if blur_radius:
        text_clip = blur_text_clip(text_clip, blur_radius)

    text_cache[arg_hash] = text_clip.copy()

    return text_clip

def create_text_chars(
    text: Union[List[Word], List[Character]],
    fontsize: int,
    color: str,
    font: str,
    bg_color: str = 'transparent',
    blur_radius: int = 0,
    opacity: float = 1,
    stroke_color: Optional[str] = None,
    stroke_width: int = 1,
    add_space_between_words: bool = True,
) -> List[VideoClip]:
    # Create a clip for each character
    clips = []
    for i, item in enumerate(text):
        if isinstance(item, Word):
            chars = item.characters
            if add_space_between_words and i < len(text) - 1:
                chars.append(Character(" ", item.color))
        else:
            chars = [item]

        for char in chars:
            clip = create_text(char.text, fontsize, char.color or color, font, bg_color, blur_radius, opacity, stroke_color, stroke_width)
            clips.append(clip)

    return clips

def create_composite_text(text_clips: List[VideoClip], font: str, font_size: int) -> CompositeVideoClip:
    clips = []

    font = ImageFont.truetype(font, font_size)
    scale_factor = 3.012 # factor to convert Pillow to MoviePy width

    full_width = 0
    for clip in text_clips[:-1]:
        width = font.getlength(clip.text) * scale_factor
        full_width += width

    full_width += text_clips[-1].size[0]
    offset_x = 0

    for clip in text_clips:
        clip.size = (int(full_width), clip.size[1])
        clip = clip.set_position((int(offset_x), 0))
        width = font.getlength(clip.text)
        offset_x += width * scale_factor
        clips.append(clip)

    return CompositeVideoClip(clips)

def str_to_charlist(text: str) -> List[Character]:
    return [Character(char) for char in text]

def create_text_ex(
    text: Union[List[Word], List[Character], str],
    fontsize: int,
    color: str,
    font: str,
    bg_color: str = 'transparent',
    blur_radius: int = 0,
    opacity: float = 1,
    stroke_color: Optional[str] = None,
    stroke_width: int = 1,
    kerning: float = 0,
) -> CompositeVideoClip:
    if isinstance(text, str):
        text = str_to_charlist(text)
    text_clips = create_text_chars(text, fontsize, color, font, bg_color, blur_radius, opacity, stroke_color, stroke_width)
    return create_composite_text(text_clips, font, fontsize // 3)
