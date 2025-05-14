import yt_dlp
import whisper

def download_audio(url, output_path="audio_files/audio"):
    codec = "mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec,
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.download([url])
        except:
            result = 1
            raise Exception(f"yt-dlp failed to download the file: {url}")
        if result != 0:
            raise Exception(f"yt-dlp failed to download the file: {url}")
       
    return f"{output_path}.{codec}"

def transcribe_audio(audio_path, lang="en"):
    model = whisper.load_model("base")
    #model = whisper.load_model("base", device="cuda") # only with CUDA and Nvidia GPU 
    result = model.transcribe(audio_path, language=lang)
    return result["text"]
