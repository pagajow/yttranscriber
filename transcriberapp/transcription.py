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
            info = ydl.extract_info(url, download=True)
            return {
                "success": True,
                "file_path": f"{output_path}.{codec}",
                "title": info.get("title"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "filesize": info.get("filesize"),
                "thumbnail": info.get("thumbnail"),
                "description": info.get("description"),
                "original_url": info.get("webpage_url"),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
       

def transcribe_audio(audio_path, lang="en"):
    try:
        model = whisper.load_model("base")
        #model = whisper.load_model("base", device="cuda") # only with CUDA and Nvidia GPU 
        result = model.transcribe(audio_path, language=lang)
        return {
            "success": True,
            "text": result["text"],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
