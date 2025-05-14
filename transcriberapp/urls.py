from django.urls import path
from .views import (
    RequestSummaryView,
    AskAIView,
    TranscriptionView,
    TranscriptionInProcessView,
    TranscriptionListView,
    TranscriptionDetailView,
    TranscriptionUpdateView,
    TranscriptionDeleteView,
)

app_name = "transcriberapp"

urlpatterns = [
    path("", TranscriptionView.as_view(), name="transcribe"),
    path("processing/", TranscriptionInProcessView.as_view(), name="transcription_in_process"),
    path("transcription/<int:pk>/ask_ai/", AskAIView.as_view(), name="ask_ai"),
    path("transcription/<int:pk>/summary-request/", RequestSummaryView.as_view(), name="request_summary"),
    path("transcriptions/", TranscriptionListView.as_view(), name="transcription_list"),
    path("transcriptions/<int:pk>/", TranscriptionDetailView.as_view(), name="transcription_detail"),
    path("transcriptions/<int:pk>/edit/", TranscriptionUpdateView.as_view(), name="transcription_edit"),
    path("transcriptions/<int:pk>/delete/", TranscriptionDeleteView.as_view(), name="transcription_delete"),
]
