# default font config
DEFAULT_FONT = "SourceSans3-Black.ttf"
DEFAULT_FONT_SIZE = 50
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
DEFAULT_PADDING_EMOJI = 5

# default highlight config
DEFAULT_HIGHLIGHT_CURRENT_WORD = True
DEFAULT_WORD_HIGHLIGHT_COLOR = "red"

# default position config
DEFAULT_POSITION = "center"

# whisperx config
MODEL = "large-v3-turbo"
DEVICE = "cpu" 
BATCH_SIZE = 16 # reduce if low on GPU mem
COMPUTE_TYPE = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)

# emojis store directory
EMOJIS_DIR = "shortcap/assets/emojis/"