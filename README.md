# shortcap

Add automatic captions to YouTube & TikTok Shorts (and other videos) using Whisper and MoviePy.

## Demo

![Demo](demo/demo.gif)

## Quick Start

Install shortcap:

```bash
pip install shortcap
```

Set required environment variables for OpenAI API:

```bash
export OPENAI_BASE_URL="your_openai_base_url"
export OPENAI_API_KEY="your_openai_api_key"
```

Use the command-line interface:

```bash
shortcap <video_file> <output_file>
```

## Features

- Automatic speech recognition using OpenAI's Whisper
- Customizable caption styling
- Support for local Whisper model or OpenAI API
- Command-line interface and programmatic usage

## Example

```bash
shortcap input.mp4 output.mp4 --font-size 80 --font-color white --stroke-width 2 --stroke-color black --highlight-current-word --word-highlight-color yellow --line-count 2 --verbose
```

## Programmatic Usage

```python
import shortcap
shortcap.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
)
```

## Custom Configuration

You can customize various aspects of the captions:

```python
import shortcap
shortcap.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
    font = "/path/to/your/font.ttf",
    font_size = 130,
    font_color = "yellow",
    stroke_width = 3,
    stroke_color = "black",
    shadow_strength = 1.0,
    shadow_blur = 0.1,
    highlight_current_word = True,
    word_highlight_color = "red",
    line_count=1,
    padding = 50,
    position = "center"
)
```

The `position` parameter allows you to control where the captions appear on the video.

Vertical position: "top", "center", "bottom", or an integer value

For example:
- `position = "top"`:  Centers the text horizontally and places it at the top of the video
- `position = "center"`:  Centers the text horizontally and places it at the center of the video
- `position = "bottom"`:  Centers the text horizontally and places it at the bottom of the video
- `position =  100`: Centers the text horizontally and places it 100 pixels from the top of the video

The default value is `"center"`, which centers the text both horizontally and vertically.

## Using Whisper Locally

By default, OpenAI Whisper is used locally if the `openai-whisper` package is installed. Otherwise, the OpenAI Whisper API is used. To force the use of the API:

```python
shortcap.add_captions(
video_file="my_short.mp4",
output_file="my_short_with_captions.mp4",
use_local_whisper=False,
)
```


Install shortcap with local Whisper support:

```bash
pip install shortcap[local_whisper]
```

## Command-line Options

For a full list of command-line options, run:

```bash
shortcap --help
```


## Changelog

For a detailed list of changes and version updates, please refer to the [CHANGELOG.md](CHANGELOG.md) file.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.

---

For more detailed information on usage and configuration, please refer to the documentation.