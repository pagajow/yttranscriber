import glob
import os
import uuid
import re
from openai import OpenAI
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView

from transcriberapp.forms import SummaryRequestForm, TranscriptionForm, TranscriptionRequestForm
from transcriberapp.models import Transcription
from transcriberapp.transcription import download_audio, transcribe_audio

import threading

transcription_lock = threading.Lock()

# Create your views here.
class TranscriptionView(FormView):
    template_name = "transcriberapp/transcription_form.html"
    form_class = TranscriptionRequestForm
    success_url = reverse_lazy("transcription")
    
    def form_valid(self, form):
        if not transcription_lock.acquire(blocking=False):
            return HttpResponseBadRequest("Another transcription is already in progress.")

        url = form.cleaned_data["url"]
        lang = form.cleaned_data["language"]

        def process_task(url, lang):
            try:
                uid = uuid.uuid4().hex
                base_path = f"audio_files/{uid}"
                audio_path = download_audio(url, base_path)
                text = transcribe_audio(audio_path, lang)

                Transcription.objects.create(
                    url=url,
                    language=lang,
                    text=text,
                    summary="",
                )

                for f in glob.glob(f"{base_path}*"):
                    os.remove(f)
            except Exception as e:
                print(f"Error during transcription: {e}")
            finally:
                transcription_lock.release()

        threading.Thread(target=process_task, args=(url, lang)).start()

        return redirect("transcriberapp:transcription_in_process")
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_label"] = "Transcribe"
        return context        
    
    def get_embed_yt_url(self, youtube_url):
        match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        return None
            
            
            
def async_summary(transcription, user_prompt, language_code, model):
    prompt_content = (
        f"User's request: {user_prompt}\n\n"
        f"Please respond in the language: {language_code}.\n"
        f"Use the following transcription as context:\n\n{transcription.text}"
    )

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful summarizer and responder."},
                {"role": "user", "content": prompt_content},
            ]
        )

        summary_text = response.choices[0].message.content
        transcription.summary = summary_text
        transcription.save()

    except Exception as e:
        print(f"Failed to get summary from OpenAI: {e}")
                    
class RequestSummaryView(View):
    def post(self, request, pk):
        form = SummaryRequestForm(request.POST)
        transcription = get_object_or_404(Transcription, pk=pk)

        if not form.is_valid():
            return HttpResponseBadRequest("Invalid form input")
        
        if "OPENAI_API_KEY" not in os.environ:
            return HttpResponseBadRequest("OpenAI API key is not set in the environment variables.")

        user_prompt = form.cleaned_data["prompt"]
        language = form.cleaned_data["language"]
        model = form.cleaned_data["model"]

        thread = threading.Thread(
            target=async_summary,
            args=(transcription, user_prompt, language, model),
            daemon=True
        )
        thread.start()

        return redirect("transcriberapp:transcription_detail", pk=transcription.pk)            
            
#-------------------------------------------            
class TranscriptionListView(ListView):
    model = Transcription
    template_name = "transcriberapp/transcription_list.html"
    context_object_name = "transcriptions"
    
    def get_queryset(self):
        return Transcription.objects.order_by("-created_at")

class TranscriptionDetailView(DetailView):
    model = Transcription
    template_name = "transcriberapp/transcription_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["openai_api_key_present"] = "OPENAI_API_KEY" in os.environ
        context["summary_form"] = SummaryRequestForm()
        return context

class TranscriptionUpdateView(UpdateView):
    model = Transcription
    form_class = TranscriptionForm 
    template_name = "transcriberapp/transcription_form.html"
    success_url = reverse_lazy("transcriberapp:transcription_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_label"] = "Save"
        return context


class TranscriptionDeleteView(DeleteView):
    model = Transcription
    template_name = "transcriberapp/transcription_confirm_delete.html"
    success_url = reverse_lazy("transcriberapp:transcription_list")
    
class TranscriptionInProcessView(TemplateView):
    template_name = "transcriberapp/transcription_in_progress.html"
    
class AskAIView(TemplateView):
    template_name = "transcriberapp/transcription_ask_ai.html"
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context["openai_api_key_present"] = "OPENAI_API_KEY" in os.environ
        context["summary_form"] = SummaryRequestForm()
        context["transcription"] = get_object_or_404(Transcription, pk=pk)
        return context