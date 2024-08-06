import praw
import movis
import string
import ffmpeg
import random
import yt_dlp
import whisper
import pyttsx3
import subprocess
from moviepy.editor import *
from moviepy.config import change_settings
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


IMAGEMAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})

# Configuration

client_id = 'ADKTOWjCN3nK6pJP32OCPQ'
client_secret = '49Hg3Ml5UxSapXVyPqRkivfaB6-rfg'
client_device = 'iPhone-X'

# Get Reddit Post

def get_reddit_post():
    reddit_instance = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=client_device)
    subreddit_instance = reddit_instance.subreddit('amItheasshole')

    submissions = []

    for submission in subreddit_instance.hot():
        submissions.append(submission)

    return random.choice(submissions)

# Text processing functions

def santizie_text(text):
    return ''.join(char for char in text if char not in string.punctuation)

def remove_periods(text):
    return text.replace('.', '')
def process_text(text, replacement="Am I the A hole"):
    return text.replace("AITA", replacement).replace("AITAH", replacement).replace("WIBTA", replacement)

# Download YouTube Video

def download_youtube_video(link, filename):
    ydl_opts = {
        'outtmpl': filename
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Text to speech

def text_to_spech(text, filename):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, filename)
    engine.runAndWait()

# Create Captions

def create_captions(audio_file, filename):
    model = whisper.load_model('base')
    result = model.transcribe(audio_file, word_timestamps=True)

    start_times = []
    end_times = []
    words = []

    for segment in result['segments']:
        for word in segment['words']:
            start_times.append(word['start'])
            end_times.append(word['end'])
            words.append(word['word'])

    movis.subtitle.write_srt_file(start_times, end_times, words, filename)

# Trim Video

def trim_video(video, start, end, filename):
    ffmpeg_extract_subclip(video, start, end, filename)

# Combine Audio, Video
def combine(audio, video, output):
    cmd = f'ffmpeg -i {video} -i {audio} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {output}'
    subprocess.call(cmd, shell=True)
    print('Muxing Done')

# Add Subtitles to video
def subtitle_video(video, subtitles, output):
    (
        ffmpeg
        .input(video)
        .output(output, vf=f'subtitles={subtitles}:force_style=Alignment=10', b='2000k', preset='fast', threads=4, vcodec='h264_qsv')
        .run()
    )


# Post to YouTube

def post_to_youtube():
    pass

def create_video():
    submission = get_reddit_post() # Getting the post
    download_youtube_video('https://www.youtube.com/watch?v=SrKiHTnLlLg&ab_channel=pungo', 'background.mp4') # Downloading the background video
    text = submission.title + submission.selftext # Combining the text
    #text = santizie_text(text) # Remove punctuation
    text = process_text(text) # Replace AITA/WIBTA with Am I the a-hole
    text = remove_periods(text)
    text_to_spech(text, 'content.mp3') # Converting to text-to-speech
    audio_duration = AudioFileClip("content.mp3").duration # Getting the audio clip
    trim_video('background.mp4', 0, audio_duration, 'trimmed.mp4') # Trimming the video
    print('doing subtitles')
    create_captions('content.mp3', 'captions.srt')
    subtitle_video('trimmed.mp4', 'captions.srt', 'captioned_video.mp4') # Captioning the video
    print('combining videos')
    combine('content.mp3', 'captioned_video.mp4', 'final_video.mp4') # Combining the videos

    # Removing extra files

    os.remove('background.mp4')
    os.remove('captioned_video.mp4')
    os.remove('captions.srt')
    os.remove('content.mp3')
    os.remove('trimmed.mp4')

create_video()