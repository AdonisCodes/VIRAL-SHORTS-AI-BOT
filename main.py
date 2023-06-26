import datetime
from youtube_transcript_api import YouTubeTranscriptApi
import math
from format_h import *
import pathlib
import random
import subprocess
import time
import cv2
import pysrt
import requests
import whisper
from moviepy.editor import *
from moviepy.video.fx.crop import crop
from moviepy.video.tools.subtitles import SubtitlesClip
from pytube import YouTube

import constants
from gpt import split_analyze, generate_emoji, generate_image

# Set the path to the Image Magic Library
os.environ["IMAGEMAGICK_BINARY"] = constants.image_magic_bin

# Set up the Whisper Transcribe instance
model = whisper.load_model("small")


# Function to convert a video to an mp3 file
def video2mp3(video_file, output_ext="mp3"):
    # Getting the Video file name
    filename, ext = os.path.splitext(video_file)

    # Extract the Audio from the Video File
    print("Extracting audio from Video File...")
    subprocess.call(
        ["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    return f"{filename}.{output_ext}"


# Function to Animate the Captions of the video
def animate_text(txt, theme, video):
    # Create a TextClip instance
    print("Creating TextClip instance...")
    text_clip = TextClip(txt, font=theme["font"], fontsize=50, color=theme["color"],
                         bg_color=theme["background"], method="caption",
                         size=(math.floor(video.size[0] * 0.9), None))

    # Adding the animation to the TextClip
    animated_text = text_clip
    if theme.get("animation"):
        if theme["animation"] == "fade":
            animated_text = text_clip.set_duration(video.duration).crossfadein(0.5).crossfadeout(0.5)

    # TODO: Create Pop animation
    # TODO: Create Slide animation
    # TODO: Create Slight Wiggle animation
    return animated_text


# Function to analyze the given Audio File and Extract the Transcript
def analyze_audio(path):
    # Analysing the audio
    print("Analyzing Audio")
    options = dict(beam_size=1, best_of=1)  # Set best_of to 1
    translate_options = dict(task="translate", **options)
    result = model.transcribe(path, **translate_options)
    return result


# Function to write a Srt File, and return the path
def write_srt(result, index):
    # Write the Srt File
    print("Starting to Write the Srt File")
    subtitle_path = constants.temp_folder + "/" + f"{index}.srt"
    subs = pysrt.SubRipFile()
    segments = result["segments"]
    start_time = ""
    end_time = ""
    text = ""

    # Loop through the segments, and write the segments
    print("Looping over Transcript Segments...")
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        sub = pysrt.SubRipItem(
            index=len(subs) + 1,
            start=pysrt.SubRipTime(seconds=start_time),
            end=pysrt.SubRipTime(seconds=end_time),
            text=text,
        )
        subs.append(sub)

    # Save the Generated Srt File
    subs.append(pysrt.SubRipItem(index=len(subs) + 1, start=pysrt.SubRipTime(seconds=start_time),
                                 end=pysrt.SubRipTime(seconds=end_time), text=text, ))
    subs.save(subtitle_path, encoding="utf-8")

    # Return the path
    return subtitle_path


# Function to add the Captions to the Video
def translate(input_video, theme, i):
    # Extracting the Audio
    audio_file = video2mp3(input_video)

    # Analyzing the Audio
    result = analyze_audio(audio_file)

    # Creating the Srt File
    subtitle_path = write_srt(result, i)

    # Set the path to where the Output Video Needs to be saved
    output_video = constants.temp_folder + "/" + f"out{i}_subtitled.mp4"

    # Create a Video instance to add the Captions
    video = VideoFileClip(input_video)

    # Adding the Captions
    print("Adding The Captions...")
    generator = lambda txt: animate_text(txt, theme, video)

    # Generate the subtitles with animated text
    subs = SubtitlesClip(subtitle_path, generator)
    subtitles = SubtitlesClip(subs, generator)

    # Adding Overlays To the Output Video
    result = video
    result = add_overlays(theme, video, result)

    # Compositing the Output Video
    comp = CompositeVideoClip([result, subtitles.set_pos(("center", math.floor(video.size[1] * 0.67)))])

    # Adding the Outro to the Output Video
    if theme.get("outro") is not None:
        outro = VideoFileClip(theme["outro"])
        comp = concatenate_videoclips([comp, outro])

    # Writing the Output Video
    comp.write_videofile(output_video)

    # Returning The Subtitle Path
    return subtitle_path


def add_captions_overlays(input, theme, i):
    # Generating the Captions
    input_video = input
    output_video = translate(input_video, theme, i)
    print("Subtitle video generated:", output_video)
    return output_video


# add_captions_overlays(r"C:\Users\Delay\Desktop\projects\Pylit2.0\src\tests\temp\out1.mp4", theme=themes[2])


# Function to Download a YouTube video from Given URL
def download_content(ur):
    # Downloading the YouTube Video
    print("Downloading YouTube video...")
    url = YouTube(ur)
    video = url.streams.get_highest_resolution()
    video_filepath = constants.temp_folder
    video.download(video_filepath, max_retries=30)

    # Returning the Video Path
    return video_filepath + '/' + video.default_filename

# Function to Analyze Captions
def analyze_captions(captions):
    # Analyzing The Captions
    print("Analyzing Captions...")
    captions = captions[0:len(captions)]
    cap = split_analyze(captions)
    print(cap)

    # Returning the Analyzed Parts
    return cap


# Function to Clip the Viral Parts from a Video
def clip_out(input, locations):
    # Load a video File
    video = VideoFileClip(input)

    # Clipping the Parts
    print("Clipping the Parts...")
    i = 0
    for location in locations:
        # Try to convert the Location TimeStamps to Float numbers
        try:
            start_time = float(location["start_time"])
            end_time = float(location["end_time"])
            duration = float(location["duration"])
        # If the Location TimeStamps are Invalid Skip the Location
        except:
            continue

        print("Doing Important Checks...")
        # Checking if the Timestamp is Correct
        if end_time - start_time < 10:
            continue
        # Checking if the Timestamp is than the Video Duration
        if end_time > video.duration:
            break

        # Cutting the Video Clip
        print("Cutting the Video Clip")
        cut = video.subclip(start_time, end_time if duration > 20 else start_time + 30)
        print("3")
        cut.write_videofile(constants.temp_folder + "/" + f"{i}.mp4", codec="libx264")
        i += 1

    # Returning the Amount of Clips created
    return i


# Function to detect Faces every Second
def detect_faces(video):
    # Initializing the OpenCV Face detection Functions
    print("Initializing Face Detection Library...")
    cascade_path = pathlib.Path(cv2.__file__).parent.absolute() / "data/haarcascade_frontalface_alt2.xml"
    clf = cv2.CascadeClassifier(str(cascade_path))
    camera = cv2.VideoCapture(video)

    # Getting Video Metadata to Do calculations
    vid = VideoFileClip(video)
    fps = vid.fps

    # Capturing the Face Locations
    print("Capturing Face Location...")
    face_locations = []
    for i in range(int(fps) * math.floor(vid.duration)):
        if i % 30 != 0:
            continue
        # Return the locations of the face/s
        ret, frame = camera.read()

        # Check if a frame was returned
        if not ret:
            break

        # detect face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = clf.detectMultiScale(gray, scaleFactor=1.03, minNeighbors=15, minSize=(40, 40),
                                    flags=cv2.CASCADE_SCALE_IMAGE)

        for (x, y, width, height) in face:
            face_locations.append([x, y, width, height])
            print("Location:", x, y, width, height)

    # Savely Closing Open Instances, and returing the Face Locations
    camera.release()
    cv2.destroyAllWindows()
    return face_locations


# Function to add Stickers to the Video
def add_stickers(sticker, subtitles, video, i, tsfx):
    print("Adding Stickers...")
    # see what type of sticker will be used
    vid = VideoFileClip(video)
    subs = pysrt.open(subtitles)

    # Get the Subtitles in "Pythonic" format
    print("Getting subtitles...")
    srt_items = []
    for sub in subs:
        start_time = (datetime.timedelta(hours=sub.start.hours, minutes=sub.start.minutes, seconds=sub.start.seconds,
                                         milliseconds=sub.start.milliseconds)).total_seconds()
        end_time = (datetime.timedelta(hours=sub.end.hours, minutes=sub.end.minutes, seconds=sub.end.seconds,
                                       milliseconds=sub.end.milliseconds)).total_seconds()
        srt_items.append({
            'start_time': start_time,
            'end_time': end_time,
            'text': sub.text
        })

    # Checking if sticker type is of Type Emoji
    if sticker == "emoji":
        # Creating Intervals to be used for Emoji placement
        interval = random.randint(1, math.floor(len(srt_items) / 2))
        print("Emoji Interval: " + str(interval))

        # Adding the Emoji
        print("Adding Emoji to Video...")
        emoji_clips = []
        for index, item in enumerate(srt_items):
            if index % interval != 0:
                continue

            # Generate the emoji
            print("Generating Emoji...")
            time.sleep(20)
            emoji = generate_emoji(item["text"])

            # Add the Emoji Using Text Clips
            print("Adding Emoji Using Text Clips...")
            emoji_clip = TextClip(emoji, fontsize=random.randint(200, 300),
                                  font=constants.emoji_font,
                                  method='caption', align='center')
            emoji_clip = emoji_clip.set_position(
                (random.randint(100, vid.size[0] - 100), random.randint(100, vid.size[0] - 400)))
            emoji_clip = emoji_clip.set_start(item["start_time"]).set_end(item["end_time"])
            direction = random.randint(0, 1)
            emoji_clip = emoji_clip.rotate(random.randint(0, 45) if direction == 0 else random.randint(-45, 0))

            # Setting Audio For Emoji Popup
            print("Adding Emoji Popup Audio...")
            emoji_clip = emoji_clip.set_audio(
                AudioFileClip(tsfx[random.randint(0, 2)]).set_start(item["start_time"]))
            emoji_clips.append(emoji_clip)

        # Composing Video with Emoji
        print("Composing & Writing Video with Emoji...")
        clip = CompositeVideoClip([vid] + emoji_clips)
        clip.write_videofile(constants.temp_folder + "/" + f"out{i}_final.mp4")

        # Return the Path of the generated Video
        return constants.temp_folder + "/" + f"out{i}_final.mp4"

    if sticker == "image":
        # Determine the interval for image placement
        interval = random.randint(2, math.floor(len(srt_items) / 2))
        print("Image Interval: " + str(interval))

        # Adding the image stickers
        print("Adding Image Stickers...")
        image_clips = []
        for index, item in enumerate(srt_items):
            if index % interval != 0:
                continue

            # Generate the image
            print("Generating Image...")
            time.sleep(20)
            image = generate_image(item["text"])
            image = requests.get(image)

            if image.status_code == 200:
                with open("image.png", "wb") as f:
                    f.write(image.content)

            print("Adding Image to Video...")
            # Add the image to a list using ImageClip
            new_size = math.floor(vid.size[0] * 0.9)
            image_clip = ImageClip("image.png")  # Create a video clip with only the image, disabling audio
            image_clip = image_clip.resize((new_size, new_size))
            image_clip = image_clip.set_position(("center", vid.size[1] * 0.05))
            image_clip = image_clip.set_start(item["start_time"]).set_end(item["end_time"])
            image_clip = image_clip.set_audio(AudioFileClip(tsfx[random.randint(0, 2)]).set_start(item["start_time"]))
            image_clips.append(image_clip)

        print("Compositing & Writing Video Clip...")
        clip = CompositeVideoClip([vid] + image_clips)
        clip.write_videofile(constants.temp_folder + "/" + f"out{i}_final.mp4")

        # Return the path of the generated video
        return constants.temp_folder + "/" + f"out{i}_final.mp4"


# Function to crop The video with the Given Face Locations
def crop_vid(input, locations, output, i):
    # Setting UP some Information to do Calculations
    theme = random.choice(constants.video_themes)
    video = VideoFileClip(input)
    height = video.size[1]
    width = height * (9 / 16)
    clips = []
    cur_time = 0

    # Edge case Handling if there is NO Face Locations
    print("Checking for Edge Case...")
    prev_middle = None
    if len(locations) - 1 < 0:
        print("Doing the Edge Case...")
        locations.append([width // 2 - (0.5 * width), 0, width // 2 + (0.5 * width), 0])

    # Starting the Cropping Process
    print("Started Cropping...")
    for i in range(len(locations)):
        sub = video.subclip(cur_time, cur_time + (video.duration / len(locations)))
        bottom_x = locations[i][0] + locations[i][2]
        middle_x = (locations[i][0] + bottom_x) // 2

        # Doing Checks
        print("Doing Important Checks...")
        if prev_middle is not None:
            if middle_x - prev_middle > 20 or middle_x - prev_middle < -20:
                middle_x = (middle_x + prev_middle) // 2
                prev_middle = middle_x

        # Cropping & Resizing
        print("Cropping and Resizing Subclip...")
        x1 = middle_x - (0.5 * width)
        x1 = x1 if x1 >= 0 else 0
        x2 = middle_x + (0.5 * width)
        x2 = x2 if x2 <= video.size[0] else video.size[0]
        cropped = crop(sub, y1=0, y2=height - 1, x1=math.floor(x1), x2=math.floor(x2))
        resized = cropped.resize(newsize=(720, 1280))

        # Appending the Subclip to the Clips list
        clips.append(resized)
        print(f"Cropped Clip {i}")
        cur_time += sub.duration

    # Concatenating the Clips & Writing Final Video file
    print("Concatenating Clips and Writing Final Video...")
    final_clip = concatenate_videoclips(clips, method='chain')
    final_clip.write_videofile(output, codec='libx264')

    # Adding the stickers / overlays
    subt = add_captions_overlays(output, theme, i)
    add_stickers(theme["sticker"], subt,
                 constants.temp_folder + "/" + f"out{i}_subtitled.mp4", i,
                 theme["sfx"])


# Function to add Overlay to the Video
def add_overlays(theme, video, result):
    print("Adding Overlays...")
    result = result
    if theme.get("overlay") is not None:
        temp = video
        overlay = VideoFileClip(theme["overlay"])
        overlay = overlay.resize(newsize=(720, 640))
        overlay = overlay.subclip(0, temp.duration)
        overlay = overlay.set_audio(None)
        overlay = overlay.set_position(("center", temp.size[1] * 0.7))
        result = CompositeVideoClip([temp, overlay])

    return result


# Functions to create the video clips
def vid_clip(link, captions):
    # Downloading the Video
    video = download_content(link)

    # Analyzing the Captions
    parts = split_analyze(f"{captions}")

    # Clipping the Video
    actual_parts_count = clip_out(video, parts)

    # Creating Short Videos from the Clips
    for i in range(actual_parts_count):
        if i >= actual_parts_count - 1:
            return actual_parts_count

        print(len(parts) - 1)
        print(f"Cropping & Adding Subtitles: Video {i}...")
        video_file = constants.temp_folder + "/" + f"{i}.mp4"
        crop_vid(video_file, detect_faces(video_file), constants.temp_folder + "/" + f"out{i}.mp4", i)

    # Returning the Amount of Shorts Created
    return actual_parts_count

def cli_interface():
    ascii_art = '''
 _   _ ___________  ___   _        _____ _   _ ___________ _____ _____     ___  _____   ______  _____ _____ 
| | | |_   _| ___ \/ _ \ | |      /  ___| | | |  _  | ___ \_   _/  ___|   / _ \|_   _|  | ___ \|  _  |_   _|
| | | | | | | |_/ / /_\ \| |      \ `--.| |_| | | | | |_/ / | | \ `--.   / /_\ \ | |    | |_/ /| | | | | |  
| | | | | | |    /|  _  || |       `--. \  _  | | | |    /  | |  `--. \  |  _  | | |    | ___ \| | | | | |  
\ \_/ /_| |_| |\ \| | | || |____  /\__/ / | | \ \_/ / |\ \  | | /\__/ /  | | | |_| |_   | |_/ /\ \_/ / | |  
 \___/ \___/\_| \_\_| |_/\_____/  \____/\_| |_/\___/\_| \_| \_/ \____/   \_| |_/\___/   \____/  \___/  \_/  
                                                                                                         
                                                                                                         '''
    
    print(ascii_art)

    video_link = input("Youtube Video Link: ")
    captions = YouTubeTranscriptApi.get_transcript(parse_vlink(video_link))
    vid_clip(video_link, captions)


cli_interface()