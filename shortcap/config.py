import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1/')

# default font config
DEFAULT_FONT = "TitanOne-Regular.ttf"
DEFAULT_FONT_SIZE = 100
DEFAULT_FONT_COLOR = "yellow"

# default stroke config
DEFAULT_STROKE_WIDTH = 3
DEFAULT_STROKE_COLOR = "black"

# default shadow config
DEFAULT_SHADOW_STRENGTH = 1.0
DEFAULT_SHADOW_BLUR = 0.1

# default subtitle config
DEFAULT_LINE_COUNT = 2
DEFAULT_PADDING = 50

# default highlight config
DEFAULT_HIGHLIGHT_CURRENT_WORD = True
DEFAULT_WORD_HIGHLIGHT_COLOR = "red"

# default position config
DEFAULT_POSITION = "center"

def get_openai_api_key() -> str:
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    return OPENAI_API_KEY

def get_openai_api_base() -> str:
    return OPENAI_BASE_URL
