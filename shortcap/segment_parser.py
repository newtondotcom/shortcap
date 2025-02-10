from typing import List, Dict, Callable, Any
import logging

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
    allow_partial_sentences: bool = False,
) -> List[Dict[str, Any]]:
    try:
        captions = []
        caption = {
            "start": None,
            "end": 0,
            "words": [],
            "text": "",
        }

        # Merge words that are not separated by spaces
        for s, segment in enumerate(segments):
            for w, word in enumerate(segment["words"]):
                if w > 0 and word["word"][0] != " ":
                    segments[s]["words"][w-1]["word"] += word["word"]
                    segments[s]["words"][w-1]["end"] = word["end"]
                    del segments[s]["words"][w]

        # Parse segments into captions that fit on the video
        for segment in segments:
            for word in segment["words"]:
                if caption["start"] is None:
                    caption["start"] = word["start"]

                text = caption["text"]+word["word"]

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