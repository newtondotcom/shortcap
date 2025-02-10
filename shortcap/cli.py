#!/usr/bin/env python3

import sys
import os
import argparse
import logging
import time

# Add the parent directory of 'shortcap' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shortcap.add_captions import add_captions
from shortcap.config import (
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

logger = logging.getLogger('shortcap.cli')

def main():
    parser = argparse.ArgumentParser(description="Add captions to a video file.")
    parser.add_argument("video_file", help="Path to the input video file")
    parser.add_argument("output_file", help="Path to the output video file")
    
    # Add more command line options
    parser.add_argument("--font", default=DEFAULT_FONT, help="Font file path")
    parser.add_argument("--font-size", type=int, default=DEFAULT_FONT_SIZE, help="Font size")
    parser.add_argument("--font-color", default=DEFAULT_FONT_COLOR, help="Font color")
    parser.add_argument("--stroke-width", type=int, default=DEFAULT_STROKE_WIDTH, help="Stroke width")
    parser.add_argument("--stroke-color", default=DEFAULT_STROKE_COLOR, help="Stroke color")
    parser.add_argument("--highlight-current-word", action="store_true", default=DEFAULT_HIGHLIGHT_CURRENT_WORD, help="Highlight the current word")
    parser.add_argument("--word-highlight-color", default=DEFAULT_WORD_HIGHLIGHT_COLOR, help="Word highlight color")
    parser.add_argument("--line-count", type=int, default=DEFAULT_LINE_COUNT, help="Maximum number of lines")
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING, help="Padding around the text")
    parser.add_argument("--position", default=DEFAULT_POSITION, help="Vertical position of the text")
    parser.add_argument("--shadow-strength", type=float, default=DEFAULT_SHADOW_STRENGTH, help="Shadow strength")
    parser.add_argument("--shadow-blur", type=float, default=DEFAULT_SHADOW_BLUR, help="Shadow blur")
    parser.add_argument("--use-local-whisper", choices=["auto", "true", "false"], default="auto", help="Use local Whisper model")
    parser.add_argument("--initial-prompt", help="Initial prompt for transcription")
    parser.add_argument("--log-file", help="Path to log file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Increase output verbosity")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

    start_time = time.time()

    try:
        use_local_whisper = None if args.use_local_whisper == "auto" else (args.use_local_whisper == "true")

        add_captions(
            args.video_file, 
            args.output_file, 
            font=args.font,
            font_size=args.font_size,
            font_color=args.font_color,
            stroke_width=args.stroke_width,
            stroke_color=args.stroke_color,
            highlight_current_word=args.highlight_current_word,
            word_highlight_color=args.word_highlight_color,
            line_count=args.line_count,
            padding=args.padding,
            position=args.position,
            shadow_strength=args.shadow_strength,
            shadow_blur=args.shadow_blur,
            print_info=args.verbose,
            initial_prompt=args.initial_prompt,
            use_local_whisper=use_local_whisper,
        )
        logger.info(f"Captions added successfully. Output saved to {args.output_file}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
