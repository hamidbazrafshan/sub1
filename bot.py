# coding: utf-8
import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from vosk import Model, KaldiRecognizer
import json
from pydub import AudioSegment

#  ‰Ÿ?„« 
TOKEN = "7654082878:AAFlsU5xiC3_WBieN1fxqEjTQnFW-nHK4qk"  VOSK_MODEL_PATH = "model-fa"  

def start(update: Update, context: CallbackContext):
    update.message.reply_text("?? ”·«„! ?ò Ê?œ?Ê? ? œﬁ?ﬁÂù«? »›—” ?œ  « “?—‰Ê?” ›«—”? «÷«›Â ò‰„.")

def handle_video(update: Update, context: CallbackContext):
    # œ—?«›  Ê?œ?Ê «“ ò«—»—
    video = update.message.video
    file_id = video.file_id
    video_file = context.bot.get_file(file_id)
    video_path = f"temp_{file_id}.mp4"
    video_file.download(video_path)
    
    update.message.reply_text("?? Ê?œ?Ê œ—?«›  ‘œ! œ— Õ«· Å—œ«“‘...")
    
    try:
        # ?. «” Œ—«Ã ’œ« «“ Ê?œ?Ê »« FFmpeg
        audio_path = extract_audio(video_path)
        
        # ?.  »œ?· ê› «— »Â „ ‰ »« Vosk
        text = convert_speech_to_text(audio_path)
        
        # ?. «÷«›Â ò—œ‰ “?—‰Ê?” »Â Ê?œ?Ê
        output_video = add_subtitle(video_path, text)
        
        # ?. «—”«· Ê?œ?Ê? ‰Â«??
        update.message.reply_video(video=open(output_video, 'rb'))
        
    except Exception as e:
        update.message.reply_text(f"? Œÿ«: {str(e)}")
    finally:
        # Å«ò ò—œ‰ ›«?·ùÂ«? „Êﬁ 
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
    return result.get("text", "„ ‰?  ‘Œ?’ œ«œÂ ‰‘œ.")

def add_subtitle(video_path: str, text: str) -> str:
    subtitle_path = video_path.replace(".mp4", ".srt")
    output_path = video_path.replace(".mp4", "_subtitled.mp4")
    
    # ”«Œ  ›«?· “?—‰Ê?”
    with open(subtitle_path, "w", encoding="utf-8") as f:
        f.write(f"1\n00:00:00,000 --> 00:01:00,000\n{text}")
    
    # «÷«›Â ò—œ‰ “?—‰Ê?” »Â Ê?œ?Ê
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