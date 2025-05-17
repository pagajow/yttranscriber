import glob
import os
import uuid
import re

from openai import OpenAI
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView

from transcriberapp.forms import SummaryRequestForm, TranscriptionForm, TranscriptionRequestForm
from transcriberapp.models import AsyncTask, AsyncTaskLog, Transcription
from transcriberapp.transcription import download_audio, transcribe_audio

import threading
from typing import Any, Callable

from django.conf import settings

transcription_lock = threading.Lock()

# Create your views here.

def async_transcription(task: AsyncTask, url:str, lang:str, callback: Callable[[AsyncTaskLog], Any]=None):
    try:
        base_path = f"{settings.MEDIA_FOLDER}/{task.task_id}"
        transcription: Transcription = task.transcription
        
        log = task.logs.create(
            message=f"Tramscription task started for URL: {url}",
            status="pending",
        )
        if callback:
            callback(log)
        
        info = download_audio(url, base_path)
        if not info.get("success", False):
            log = task.logs.create(
                message=info.get("error", "Unknown download error"),
                status="failed",
            )
            if callback:
                callback(log)
            return
            
        audio_path = info.get("file_path", None)
        thumbnail = info.get("thumbnail", None)
        title = info.get("title", None)
        duration = info.get("duration", None)
        
        transcription.title = title
        transcription.duration = duration
        transcription.thumbnail = thumbnail
        transcription.save()
        
        log = task.logs.create(
            message="Audio downloaded successfully",
            status="in_progress",
        )
        if callback:
            callback(log)
        
        result = transcribe_audio(audio_path, lang)
        if not result.get("success", False):
            log = task.logs.create(
                message=result.get("error", "Unknown transcription error"),
                status="failed",
            )
            if callback:
                callback(log)
            return

        transcription.text = result.get("text", "")
        transcription.save()
        
        log = task.logs.create(
            message="Transcription completed successfully",
            status="in_progress",
        )
        if callback:
            callback(log)

        files = []
        for f in glob.glob(f"{base_path}*"):
            files.append(f)
            os.remove(f)
        log = task.logs.create(
            message=f"Downloaded ({len(files)}) files removed.",
            status="completed",
        )
        if callback:
            callback(log)
    except Exception as e:
        log = task.logs.create(
            message=str(e),
            status="failed",
        )
        if callback:
            callback(log)
    finally:
        transcription_lock.release()

class TranscriptionView(FormView):
    template_name = "transcriberapp/transcription_form.html"
    form_class = TranscriptionRequestForm
    success_url = reverse_lazy("transcription")
    
    def form_valid(self, form):
        if not transcription_lock.acquire(blocking=False):
            return HttpResponseBadRequest("Another transcription is already in progress.")

        url = form.cleaned_data["url"]
        lang = form.cleaned_data["language"]
        transcription = Transcription.objects.create(url=url, language=lang)
        task = transcription.tasks.create(task_id=uuid.uuid4().hex, status="pending", task_type="transcription")

        threading.Thread(target=async_transcription, args=(task, url, lang)).start()

        return redirect("transcriberapp:transcription_detail", pk=transcription.pk)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submit_label"] = "Transcribe"
        return context        
            
             
def async_summary(task: AsyncTask, user_prompt:str, language_code:str, model:str, callback: Callable[[AsyncTaskLog], Any]=None):
    transcription: Transcription = task.transcription
    log = task.logs.create(
        message=f"AI request task started for transcription ID: {transcription.pk}",
        status="pending",
    )
    if callback:
        callback(log)
    
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
        
        log = task.logs.create(
            message=f"AI request completed successfully with a response of {len(summary_text)} characters",
            status="completed",
        )
        if callback:
            callback(log)
    except Exception as e:
        log = task.logs.create(
            message=f"AI request failed: {str(e)}",
            status="failed",
        )
        if callback:
            callback(log)
                    
class RequestSummaryView(View):
    def post(self, request, pk):
        form = SummaryRequestForm(request.POST)
        transcription = get_object_or_404(Transcription, pk=pk)
        task = transcription.tasks.create(task_id=uuid.uuid4().hex, status="pending", task_type="ai_request")

        if not form.is_valid():
            return HttpResponseBadRequest("Invalid form input")
        
        if "OPENAI_API_KEY" not in os.environ:
            return HttpResponseBadRequest("OpenAI API key is not set in the environment variables.")

        user_prompt = form.cleaned_data["prompt"]
        language = form.cleaned_data["language"]
        model = form.cleaned_data["model"]

        thread = threading.Thread(
            target=async_summary,
            args=(task, user_prompt, language, model),
            daemon=True
        )
        thread.start()

        return redirect("transcriberapp:transcription_detail", pk=transcription.pk)            
            
                     
def active_tasks_status(request, pk):
    transcription = get_object_or_404(Transcription, pk=pk)
    tasks = [task for task in transcription.tasks.order_by("created_at") if not task.is_done]

    data = {}
    for task in tasks:
        logs = task.logs.order_by("created_at")
        
        data[task.task_id] = {
            "task_id": task.task_id,
            "type": task.task_type,
            "status": task.status,
            "logs": [{
                "message": log.message,
                "status": log.status,  
                "id": log.pk,
                } for log in logs],
        }
    return JsonResponse(data)           
            
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
        context["active_tasks"] = [task for task in self.object.tasks.order_by("-created_at") if not task.is_done]
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
    
    
class AskAIView(TemplateView):
    template_name = "transcriberapp/transcription_ask_ai.html"
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context["openai_api_key_present"] = "OPENAI_API_KEY" in os.environ
        context["summary_form"] = SummaryRequestForm()
        context["transcription"] = get_object_or_404(Transcription, pk=pk)
        return context