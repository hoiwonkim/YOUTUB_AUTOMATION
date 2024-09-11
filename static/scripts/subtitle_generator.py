import speech_recognition as sr
from moviepy.editor import VideoFileClip
import os

def generate_subtitles(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile("temp_audio.wav")
    
    recognizer = sr.Recognizer()
    subtitles = []
    
    with sr.AudioFile("temp_audio.wav") as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            subtitles.append((0, video.duration, text))
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
    
    os.remove("temp_audio.wav")
    return subtitles