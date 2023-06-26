image_magic_bin = "C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe"  # Install ImageMagick, copy the path to
# the magick.exe, and paste it here. You probably wont have to paste it but just in case
# https://imagemagick.org/script/download.php
temp_folder = "temp"
emoji_font = "C:/Windows/Fonts/seguiemj.ttf"

video_themes = [
    {
        "color": "black",
        "font": emoji_font,
        "background": "yellow",
        "overlay": "Assets/1_overlay.mp4",
        "outro": "Assets/1_outro.mp4",
        "sticker": "emoji",
        "tsfx": ["Assets/tsfx/1.mp3",
                 "Assets/tsfx/2.mp3",
                 "Assets/tsfx/3.mp3"],
    },
    {
        "color": "white",
        "font": emoji_font,
        "background": "cyan",
        "animation": "pop",
        "overlay": None,
        "outro": "Assets/2_outro.mp4",
        "sfx": ["Assets/tsfx/3.mp3",
                "Assets/tsfx/4.mp3",
                "Assets/tsfx/5.mp3"],
    },
    {
        "color": "yellow",
        "font": emoji_font,
        "background": "transparent",
        "animation": "pop",
        "overlay": "Assets/1_overlay.mp4",
        "outro": "Assets/1_outro.mp4",
        "sticker": "emoji",
        "sfx": ["Assets/tsfx/6.mp3",
                "Assets/tsfx/7.mp3",
                "Assets/tsfx/8.mp3"]
    },
    {
        "color": "white",
        "font": emoji_font,
        "background": "black",
        "animation": "pop",
        "overlay": "Assets/3_overlay.mp4",
        "outro": "Assets/3_outro.mp4",
        "sticker": "emoji",
        "sfx": ["Assets/tsfx/9.mp3",
                "Assets/tsfx/10.mp3",
                "Assets/tsfx/1.mp3"]
    }
]

# OpenAi
op_apikey = "" # OpenAi API key here; Tutorial: https://www.youtube.com/watch?v=nafDyRsVnXU
