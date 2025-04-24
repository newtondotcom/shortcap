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


def populate_tabs(segments):
    """Extracts words and timings from transcriptions and populates 'tab'."""
    tab = []
    for s in segments:
        print(s["words"])
        exit()
        for i, word in enumerate(s["words"]):
            if i == len(s["words"]) - 1:
                tab.append({
                    "start" : word["start"],
                    "end":  word["end"],
                    "word" : word["word"],
                    "final" : True})
                # Last word in a sentence
            else:
                tab.append({
                    "start" : word["start"],
                    "end":  word["end"],
                    "word" : word["word"],
                    "final" : False})
                # Intermediate word
    return tab


def analyse_tab_durations(tab):
    """Calculates average time and length of words in 'tab' for grouping."""
    moyenne_time = 0
    moyenne_length = 0
    new_tab = []
    for word in tab:
        moyenne_time += word["end"] - word["start"]
        moyenne_length += len(word["word"])
    moyenne_length = moyenne_length / len(tab)
    moyenne_time = moyenne_time / len(tab)

    retenue = 0
    seuil = 0.10  # Proximity threshold for grouping words

    # Contain words within a group based on specified criteria
    for j, word in enumerate(tab):
        if retenue > 0:
            retenue -= 1
        else:
            retenue = group_words_based_on_threshold(
                tab, new_tab, seuil, j, word , moyenne_time, moyenne_length
            )
    return new_tab

def group_words_based_on_threshold(
    tab, new_tab, proximity_threshold, index, word, average_time, average_length
):
    """
    Groups words based on specified thresholds and criteria.
    """

    def is_word_below_threshold(word, next_word=None):
        """Checks if a word meets the threshold criteria."""
        if next_word is None:
            # Check if the word ends with "." or meets time/length criteria
            if "." in word["word"]:
                return True
            return word["end"] - word["start"] < average_time or len(word["word"]) < average_length
        else:
            # Check proximity threshold between current word and next word
            return word["end"] - word["start"] < proximity_threshold and "." not in word["word"]

    # Initialize a new group with the current word
    local_combined_words = {
        "start": word["start"],
        "end": word["end"],
        "words": [word],
        "text": word["word"],
    }

    # If the current word does not meet the threshold or is the last word in the list, append the group to new_tab
    if not is_word_below_threshold(word) or index == len(tab) - 1:
        new_tab.append(local_combined_words)
        return 0

    # Determine the number of words to juxtapose
    words_to_juxtapose = min(4, len(tab) - index)
    retenue = 0

    # Loop through subsequent words to form a group based on the threshold criteria
    for i in range(1, words_to_juxtapose):
        current_word = tab[index + i]
        previous_word = tab[index + i - 1]

        if is_word_below_threshold(current_word) and is_word_below_threshold(
            previous_word, current_word
        ) or "." in current_word["word"]:
            local_combined_words["words"].append(current_word)
            local_combined_words["end"] = current_word["end"]
            local_combined_words["text"] += " " + current_word["word"]
            retenue += 1
        else:
            break  # Stop adding words to the group if threshold is not met and not a sentence-ending word

    # Append the final group to the new_tab list
    new_tab.append(local_combined_words)
    return retenue

def check_captions(captions):
    for caption in captions:
        # Check keys exist
        if not all(key in caption for key in ["start", "end", "words","text","emoji"]):
            raise ValueError(f"""Word missing required keys ("start", "end", "words","text","emoji") for {caption}""")
        for word in caption["words"]:
            if not all(key in word for key in ["start", "end", "word"]):
                raise ValueError(f"Word missing required keys (start, end, or word) for {word} in {caption}")
    logger.info("Words array is consistent")


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
        import whisperx
        use_local_whisper = True
        if print_info:
            logger.info("Using local whisperx model...")
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
