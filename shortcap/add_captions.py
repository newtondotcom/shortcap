from typing import Optional, Callable, List, Dict, Any, Tuple, Union
from moviepy.editor import VideoFileClip, CompositeVideoClip
import subprocess
import tempfile
import time
import os
import logging
import pkg_resources

from . import segment_parser
from . import transcriber
from .text_renderer import (
    create_text_ex,
    Word,
)
from .utils import (
    ffmpeg,
    get_font_path,
    detect_local_whisper,
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
    initial_prompt: Optional[str] = None,
    segments: Optional[List[Dict[str, Any]]] = None,
    use_local_whisper: str = "auto",
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

            if use_local_whisper == "auto":
                use_local_whisper = detect_local_whisper(print_info)

            try:
                if use_local_whisper:
                    segments = transcriber.transcribe_locally(temp_audio_file, initial_prompt)
                else:
                    segments = transcriber.transcribe_with_api(temp_audio_file, initial_prompt)
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

        for caption in captions:
            captions_to_draw = []
            if highlight_current_word:
                for i, word in enumerate(caption["words"]):
                    if i+1 < len(caption["words"]):
                        end = caption["words"][i+1]["start"]
                    else:
                        end = word["end"]

                    captions_to_draw.append({
                        "text": caption["text"],
                        "start": word["start"],
                        "end": end,
                    })
            else:
                captions_to_draw.append(caption)

            for current_index, caption in enumerate(captions_to_draw):
                line_data = calculate_lines(caption["text"], font, font_size, stroke_width, text_bbox_width)

                # Calculate vertical position
                if isinstance(position, int):
                    text_y_offset = position
                elif position == "center":
                    text_y_offset = video.h // 2 - line_data["height"] // 2
                elif position == "top":
                    text_y_offset = padding
                elif position == "bottom":
                    text_y_offset = video.h - line_data["height"] - padding
                else:
                    raise ValueError("Invalid vertical position. Use 'center', 'top', 'bottom', or an integer.")

                index = 0
                for line in line_data["lines"]:
                    pos = ("center", text_y_offset)

                    words = line["text"].split()
                    word_list = []
                    for w in words:
                        word_obj = Word(w)
                        if highlight_current_word and index == current_index:
                            word_obj.set_color(word_highlight_color)
                        index += 1
                        word_list.append(word_obj)

                    # Create shadow
                    shadow_left = shadow_strength
                    while shadow_left >= 1:
                        shadow_left -= 1
                        shadow = create_shadow(line["text"], font_size, font, shadow_blur, opacity=1)
                        shadow = shadow.set_start(caption["start"])
                        shadow = shadow.set_duration(caption["end"] - caption["start"])
                        shadow = shadow.set_position(pos)
                        clips.append(shadow)

                    if shadow_left > 0:
                        shadow = create_shadow(line["text"], font_size, font, shadow_blur, opacity=shadow_left)
                        shadow = shadow.set_start(caption["start"])
                        shadow = shadow.set_duration(caption["end"] - caption["start"])
                        shadow = shadow.set_position(pos)
                        clips.append(shadow)

                    # Create text
                    text = create_text_ex(word_list, font_size, font_color, font, stroke_color=stroke_color, stroke_width=stroke_width)
                    text = text.set_start(caption["start"])
                    text = text.set_duration(caption["end"] - caption["start"])
                    text = text.set_position(pos)
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

