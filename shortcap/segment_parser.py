from typing import List, Dict, Callable, Any
import logging
from shortcap.utils import analyse_tab_durations, group_words_based_on_threshold, populate_tabs, check_captions

logger = logging.getLogger(__name__)

class SegmentParseError(Exception):
    """Custom exception for errors in segment parsing"""
    pass

def has_partial_sentence(text):
    words = text.split()
    if len(words) >= 2:
        prev_word = text.split()[-2].strip()
        if prev_word[-1] == ".":
            return True
    return False

def parse(
    segments: List[Dict[str, Any]],
    fit_function: Callable[[str], bool],
    allow_partial_sentences: bool = True,
) -> List[Dict[str, Any]]:
    try:
        #captions = []
        #words_flatten = populate_tabs(segments)
        #captions = analyse_tab_durations(words_flatten)
        #print(len(captions), len(words_flatten))
        #return captions

        captions = []
        caption = {
            "start": None,
            "end": 0,
            "words": [],
            "text": "",
        }

        for s, segment in enumerate(segments):
            for w, word in enumerate(segment["words"]):
                # Some words can't be aligned by whisperx so they dont have any "start" or "end" attributes
                if not all(key in word for key in ["start", "end"]):
                    if "start" not in word:
                        segments[s]["words"][w]["start"] = segment["words"][w - 1]["end"] if (w > 1  and "end" in segment["words"][w - 1] ) else segment["start"]
                    if "end" not in word:
                        segments[s]["words"][w]["end"] = segment["words"][w + 1]["start"] if (w+1 < len(segment["words"]) and "start" in segment["words"][w + 1] ) else  segment["end"]
                        
                # Merge words that are not separated by spaces
                #if w > 0 and word["word"][0] != " ":
                #    segments[s]["words"][w-1]["word"] += word["word"]
                 #   segments[s]["words"][w-1]["end"] = word["end"]
                 #   del segments[s]["words"][w]

        # Check that the captions follow a consistent format
        check_captions(segments)

        # Parse segments into captions that fit on the video
        for segment in segments:
            for word in segment["words"]:
                if caption["start"] is None:
                    caption["start"] = word["start"]

                text = caption["text"] + " " + word["word"]

                caption_fits = allow_partial_sentences or not has_partial_sentence(text)
                caption_fits = caption_fits and fit_function(text)

                if caption_fits:
                    caption["words"].append(word)
                    caption["end"] = word["end"]
                    caption["text"] = text
                else:
                    captions.append(caption)
                    caption = {
                        "start": word["start"],
                        "end": word["end"],
                        "words": [word],
                        "text": word["word"],
                    }

        captions.append(caption)
        return captions

    except Exception as e:
        logger.error(f"An error occurred while parsing segments: {str(e)}")
        raise SegmentParseError(f"Failed to parse segments: {str(e)}")
