# 🎙️ YT Transcriber

**YT Transcriber** is a local Django application designed to:

- download videos from YouTube (or other sources supported by `yt-dlp`),
- transcribe audio to text using the `whisper` model (locally),
- optionally generate a summary using the OpenAI API (if a key is provided).

The app **does not include a user system or authentication** and is **not intended for public hosting** — it is built as a **local personal tool**.

---

## 📦 Project Overview

This project is built using Python 3.10 and runs inside a virtual environment. It is designed to:

- be easily developed locally by developers,
- run via Docker Compose or from a prebuilt `.tar` image,
- function without internet access (except for the OpenAI API),
- work without user accounts or authentication.

---

## 🛠️ Setting Up the Environment

### 1. Create a virtual environment (Python 3.10):

```bash
python -m venv venv
````

### 2. Activate the environment:

```bash
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS
```

---

## 📚 Installing Dependencies

### Required packages:

```bash
pip install django yt-dlp openai-whisper torch ffmpeg-python django-environ openai markdown gunicorn channels channels_redis
python -m pip install --upgrade pip
```

### Package descriptions:

| Package          | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `django`         | Web framework                                             |
| `yt-dlp`         | Download video/audio from YouTube and other sources       |
| `openai-whisper` | Transcribe audio to text locally                          |
| `torch`          | ML backend required by `whisper`                          |
| `ffmpeg-python`  | Audio/video file processing and conversion                |
| `django-environ` | Manage environment variables via `.env` file              |
| `openai`         | Access OpenAI language models (e.g., GPT-4)               |
| `markdown`       | Format text using Markdown                                |
| `gunicorn`       | Production-grade WSGI server for running Django in Docker |

---

## 🔧 Additional system requirement (for local runs)

If you run the project **outside Docker**, make sure that [FFmpeg](https://ffmpeg.org/download.html) is installed on your system and accessible via command line.

You can check it by running:

```bash
ffmpeg -version
```
---

### Managing `requirements.txt`

```bash
pip freeze > requirements.txt      # Save current dependencies
pip install -r requirements.txt    # Install from file
```

---

## 🚧 Creating the Django App

```bash
django-admin startproject yttranscriber
cd yttranscriber
python manage.py startapp transcriberapp
```

In `yttranscriber/settings.py`, add the app:

```python
INSTALLED_APPS = [
    ...
    "transcriberapp",
]
```

---

## 🧠 Application Functionality

The project includes a working set of core features and provides a minimal but complete use case implementation. The following functionality has already been implemented:

- a form for submitting a video link (e.g., from YouTube),
- backend logic to download and extract audio using `yt-dlp`,
- local transcription of the audio using `openai-whisper`,
- optional summary generation if a valid OpenAI API key is provided,
- display of both the transcription and (if available) summary on the results page.

This demonstrates a basic but realistic and functioning pipeline for turning video into summarized text, fully runnable locally.

📌 **Note:** The application does **not include user authentication or account management**. It is intended as a **local tool for personal use**. Public deployment would require further work related to user access control, security, and scalability.

---

## 🐳 Building and Running the Docker Container

### 🔨 Build the Docker image locally:

```bash
docker build -t yttranscriber:latest .
```

### 💾 Save the image to a `.tar` file:

```bash
docker save -o yttranscriber.tar yttranscriber:latest
```

---

### 🔄 Load a prebuilt `.tar` image

If you've downloaded a ready-made image (`yttranscriber.tar`), load it with:

```bash
docker load -i yttranscriber.tar
```

---

## 🚀 Running the Application

With an `.env` file:

```bash
docker run --env-file .env -p 8000:8000 yttranscriber:latest
```

Or using Docker Compose:

```bash
docker compose up
```

---

## 📁 `.env` File

The user must create a `.env` file based on `.env.example`.
Required environment variables:

```
SECRET_KEY=your-secret-key
DEBUG=True
OPENAI_API_KEY=your-optional-openai-key
```

---

## 📥 Using the Prebuilt Docker Image

If you prefer not to build the image yourself, download `yttranscriber.tar` from the project root or GitHub Releases:

```bash
docker load -i yttranscriber.tar
```

---

## 📌 Summary

* The project is intended for **local execution**
* Supports transcription and optional summarization
* Can be run via Docker (from source or prebuilt `.tar` file)
* No login system — **not suitable for public servers without modification**

---


