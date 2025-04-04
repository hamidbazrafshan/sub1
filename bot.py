# coding: utf-8
import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from vosk import Model, KaldiRecognizer
import json
from pydub import AudioSegment

# ���?���
TOKEN = "7654082878:AAFlsU5xiC3_WBieN1fxqEjTQnFW-nHK4qk"  VOSK_MODEL_PATH = "model-fa"  

def start(update: Update, context: CallbackContext):
    update.message.reply_text("?? ����! ?� �?�?�? ? ��?���? �����?� �� �?���?� ����? ����� ���.")

def handle_video(update: Update, context: CallbackContext):
    # ��?��� �?�?� �� �����
    video = update.message.video
    file_id = video.file_id
    video_file = context.bot.get_file(file_id)
    video_path = f"temp_{file_id}.mp4"
    video_file.download(video_path)
    
    update.message.reply_text("?? �?�?� ��?��� ��! �� ��� ������...")
    
    try:
        # ?. ������� ��� �� �?�?� �� FFmpeg
        audio_path = extract_audio(video_path)
        
        # ?. ���?� ����� �� ��� �� Vosk
        text = convert_speech_to_text(audio_path)
        
        # ?. ����� ���� �?���?� �� �?�?�
        output_video = add_subtitle(video_path, text)
        
        # ?. ����� �?�?�? ���??
        update.message.reply_video(video=open(output_video, 'rb'))
        
    except Exception as e:
        update.message.reply_text(f"? ���: {str(e)}")
    finally:
        # �ǘ ���� ��?���? ����
        for file in [video_path, audio_path, output_video]:
            if os.path.exists(file):
                os.remove(file)

def extract_audio(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".wav")
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path
    ], check=True)
    return audio_path

def convert_speech_to_text(audio_path: str) -> str:
    model = Model(VOSK_MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)
    
    with open(audio_path, "rb") as audio_file:
        while True:
            data = audio_file.read(4000)
            if not data:
                break
            recognizer.AcceptWaveform(data)
    
    result = json.loads(recognizer.FinalResult())
    return result.get("text", "���? ���?� ���� ���.")

def add_subtitle(video_path: str, text: str) -> str:
    subtitle_path = video_path.replace(".mp4", ".srt")
    output_path = video_path.replace(".mp4", "_subtitled.mp4")
    
    # ���� ��?� �?���?�
    with open(subtitle_path, "w", encoding="utf-8") as f:
        f.write(f"1\n00:00:00,000 --> 00:01:00,000\n{text}")
    
    # ����� ���� �?���?� �� �?�?�
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={subtitle_path}:force_style='Fontsize=24,PrimaryColour=white'",
        "-c:a", "copy",
        output_path
    ], check=True)
    return output_path

if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    updater.start_polling()
    updater.idle()