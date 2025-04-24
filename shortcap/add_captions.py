from typing import Optional, Callable, List, Dict, Any, Union
from moviepy.editor import VideoFileClip, CompositeVideoClip
import subprocess
import tempfile
import time
import os
import logging
import pkg_resources

from . import emojis
from . import segment_parser
from . import transcriber
from . import utils
from .text_renderer import (
    create_text_ex,
    Word,
)
from .utils import (
    ffmpeg,
    get_font_path,
    fits_frame,
    calculate_lines,
    create_shadow,
)
from .config import (
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    DEFAULT_FONT_COLOR,
    DEFAULT_STROKE_WIDTH,
    DEFAULT_STROKE_COLOR,
    DEFAULT_HIGHLIGHT_CURRENT_WORD,
    DEFAULT_WORD_HIGHLIGHT_COLOR,
    DEFAULT_LINE_COUNT,
    DEFAULT_PADDING,
    DEFAULT_SHADOW_STRENGTH,
    DEFAULT_SHADOW_BLUR,
    DEFAULT_POSITION,
    DEFAULT_PADDING_EMOJI,
)

lines_cache = {}

logger = logging.getLogger('shortcap.add_captions')

class CaptionError(Exception):
    """Custom exception for errors in the caption process"""
    pass

def add_captions(
    video_file: str,
    output_file: str = "with_transcript.mp4",
    font: str = DEFAULT_FONT,
    font_size: int = DEFAULT_FONT_SIZE,
    font_color: str = DEFAULT_FONT_COLOR,
    stroke_width: int = DEFAULT_STROKE_WIDTH,
    stroke_color: str = DEFAULT_STROKE_COLOR,
    highlight_current_word: bool = DEFAULT_HIGHLIGHT_CURRENT_WORD,
    word_highlight_color: str = DEFAULT_WORD_HIGHLIGHT_COLOR,
    line_count: int = DEFAULT_LINE_COUNT,
    fit_function: Optional[Callable[[str], bool]] = None,
    padding: int = DEFAULT_PADDING,
    position: Union[int, str] = DEFAULT_POSITION,
    shadow_strength: float = DEFAULT_SHADOW_STRENGTH,
    shadow_blur: float = DEFAULT_SHADOW_BLUR,
    print_info: bool = False,
    segments: Optional[List[Dict[str, Any]]] = None,
    align_words : bool = True,
    language : Optional[str] = None,
) -> CompositeVideoClip:
    try:
        _start_time = time.time()

        # 修改字体处理逻辑
        if font == DEFAULT_FONT:
            font = pkg_resources.resource_filename('shortcap', 'assets/fonts/TitanOne-Regular.ttf')
        else:
            font = get_font_path(font)

        if not os.path.exists(font) and font not in ["Arial", "Helvetica"]:
            raise CaptionError(f"Font not found: {font}")

        if print_info:
            logger.info("Extracting audio...")

        temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name
        try:
            ffmpeg([
                'ffmpeg',
                '-y',
                '-i', video_file,
                temp_audio_file
            ])
        except subprocess.CalledProcessError as e:
            raise CaptionError(f"Failed to extract audio: {str(e)}")

        if segments is None:
            if print_info:
                logger.info("Transcribing audio...")
            try:
                segments, language = transcriber.transcribe_locally(temp_audio_file, align_words,language)
            except Exception as e:
                raise CaptionError(f"Failed to transcribe audio: {str(e)}")

        if print_info:
            logger.info("Generating video elements...")

        try:
            video = VideoFileClip(video_file)
        except Exception as e:
            raise CaptionError(f"Failed to open video file: {str(e)}")

        text_bbox_width = video.w - padding * 2
        clips = [video]

        captions = segment_parser.parse(
            segments=segments,
            fit_function=fit_function if fit_function else fits_frame(
                line_count,
                font,
                font_size,
                stroke_width,
                text_bbox_width,
            ),
        )
       
        captions = emojis.fetch_similar_emojis(captions, language)

        utils.check_captions(captions)
        
        for caption in captions:

            # Generate individual word-timed captions like ASS's \k tags
            captions_to_draw = []
            if highlight_current_word:
                for i, word in enumerate(caption["words"]):
                    start = word["start"]
                    end = word["end"]  # Previously : caption["words"][i + 1]["start"] if i + 1 < len(caption["words"]) else 
                    captions_to_draw.append({
                        "text": word["word"].strip(),
                        "start": start,
                        "end": end,
                        "index": i,
                    })
            else:
                captions_to_draw.append({
                    "text": caption["text"],
                    "start": caption["start"],
                    "end": caption["end"],
                    "index": -1,
                })

            for current_index, word_caption in enumerate(captions_to_draw):
                # Use text layout logic
                line_data = calculate_lines(
                    word_caption["text"], font, font_size, stroke_width, text_bbox_width
                )

                # Vertical alignment
                if isinstance(position, int):
                    text_y_offset = position
                elif position == "center":
                    text_y_offset = video.h // 2 - line_data["height"] // 2
                elif position == "top":
                    text_y_offset = padding
                elif position == "bottom":
                    text_y_offset = video.h - line_data["height"] - padding
                else:
                    raise ValueError("Invalid vertical position.")

                for i, line in enumerate(line_data["lines"]):
                    pos = ("center", text_y_offset)

                    ## Add emoji to caption above first line
                    if i == 1 and caption["emoji"] :
                        emoji_clip = emojis.create_emoji_clip(caption["emoji"]
                        ).set_start(caption["start"]).set_duration(
                        caption["end"] - caption["start"]
                        ).set_position(pos + DEFAULT_PADDING_EMOJI )
                        clips.append(emoji_clip)
                        logger.info(f"Emoji added: {caption["emoji"]}")

                    word_objects = []
                    for i, word in enumerate(line["text"].split()):
                        word_obj = Word(word)
                        if highlight_current_word and i == word_caption.get("index"):
                            word_obj.set_color(word_highlight_color)
                        word_objects.append(word_obj)

                    # Shadow layers (fading if shadow_strength isn't an int)
                    remaining_shadow = shadow_strength
                    while remaining_shadow >= 1:
                        shadow = create_shadow(
                            line["text"], font_size, font, shadow_blur, opacity=1
                        ).set_start(word_caption["start"]).set_duration(
                            word_caption["end"] - word_caption["start"]
                        ).set_position(pos)
                        clips.append(shadow)
                        remaining_shadow -= 1

                    if remaining_shadow > 0:
                        shadow = create_shadow(
                            line["text"], font_size, font, shadow_blur, opacity=remaining_shadow
                        ).set_start(word_caption["start"]).set_duration(
                            word_caption["end"] - word_caption["start"]
                        ).set_position(pos)
                        clips.append(shadow)

                    # Text clip
                    text = create_text_ex(
                        word_objects,
                        font_size,
                        font_color,
                        font,
                        stroke_color=stroke_color,
                        stroke_width=stroke_width,
                    ).set_start(word_caption["start"]).set_duration(
                        word_caption["end"] - word_caption["start"]
                    ).set_position(pos)

                    clips.append(text)
                    text_y_offset += line["height"]

        end_time = time.time()
        generation_time = end_time - _start_time

        if print_info:
            logger.info(f"Generated in {generation_time//60:02.0f}:{generation_time%60:02.0f} ({len(clips)} clips)")
            logger.info("Rendering video...")

        video_with_text = CompositeVideoClip(clips)

        try:
            video_with_text.write_videofile(
                filename=output_file,
                codec="libx264",
                fps=video.fps,
                logger="bar" if print_info else None,
            )
        except Exception as e:
            raise CaptionError(f"Failed to write output video: {str(e)}")

        end_time = time.time()
        total_time = end_time - _start_time
        render_time = total_time - generation_time

        if print_info:
            logger.info(f"Generated in {generation_time//60:02.0f}:{generation_time%60:02.0f}")
            logger.info(f"Rendered in {render_time//60:02.0f}:{render_time%60:02.0f}")
            logger.info(f"Done in {total_time//60:02.0f}:{total_time%60:02.0f}")

        return video_with_text

    except CaptionError as ce:
        logger.error(f"Caption Error: {str(ce)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise CaptionError(f"An unexpected error occurred: {str(e)}")
    finally:
        # Clean up temporary files
        if 'temp_audio_file' in locals():
            try:
                os.remove(temp_audio_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary audio file: {str(e)}")

