run:
    uv  run --active shortcap demo/anymev2.mp4 demo/output.mp4 --verbose --position=bottom

gif input output :
    ffmpeg -i {{input}}.mp4 -vf "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" {{output}}.gif