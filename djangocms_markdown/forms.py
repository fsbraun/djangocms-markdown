from django import forms

from .models import MDText
from .widgets import MarkdownEditorWidget


class MDTextForm(forms.ModelForm):
    body = forms.CharField(
        widget=MarkdownEditorWidget(),
        required=False,
    )

    class Meta:
        model = MDText
        fields = ("body",)
