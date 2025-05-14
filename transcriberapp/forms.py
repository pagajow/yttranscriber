from django import forms
from transcriberapp.models import Transcription

class TranscriptionRequestForm(forms.ModelForm):
    language = forms.ChoiceField(
        choices=Transcription.LANGUAGE_CHOICES,
        required=True,
        widget=forms.Select()
    )

    class Meta:
        model = Transcription
        fields = ["url", "language"]
        labels = {
            "url": "YouTube video link",
            "language": "Select transcription language",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["language"].initial = Transcription.LANGUAGE_CHOICES[0][0]


class TranscriptionForm(forms.ModelForm):
    language = forms.ChoiceField(
        choices=Transcription.LANGUAGE_CHOICES,
        required=True,
        widget=forms.Select()
    )

    class Meta:
        model = Transcription
        fields = ["url", "language", "text", "summary"]
        labels = {
            "url": "YouTube video link",
            "language": "Select transcription language",
            "text": "Transcription",
            "summary": "Summary",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # URL tylko do odczytu
        self.fields["url"].disabled = True

OPENAI_MODEL_CHOICES = [
    ("gpt-4o-mini", "GPT-4o Mini (Fast, affordable small model for focused tasks) - $0.15/$0.60"),
    ("gpt-4o", "GPT-4o (Fast, intelligent, flexible GPT model) - $2.50/$10.00"),
    ("gpt-4.1", "GPT-4.1 (Flagship GPT model for complex tasks) - $2.00/$8.00"),
    ("gpt-4.1-nano", "GPT-4.1 nano (Fastest, most cost-effective GPT-4.1 model) - $0.15/$0.60"),
    ("o4-mini", "o4-mini (Faster, more affordable reasoning model) - $1.10/$4.40"),
    ("o3-mini", "o3-mini (A small model alternative to o3) - $1.10/$4.40"),
    ("o1-mini", "o1-mini (A small model alternative to o1) - $1.10/$4.40"),
    ("o3", "o3 (Most powerful reasoning model) - $10.00/$40.00"),
    ("o1", "o1 (Previous full o-series reasoning model) - $15.00/$60.00"),
]

class SummaryRequestForm(forms.Form):
    prompt = forms.CharField(label="Your question or instruction", widget=forms.Textarea)
    language = forms.ChoiceField(
        label="Response language",
        choices=Transcription.LANGUAGE_CHOICES
    )
    
    model = forms.ChoiceField(
        label="OpenAI model",
        choices=OPENAI_MODEL_CHOICES,
        initial=OPENAI_MODEL_CHOICES[0][0],
    )
