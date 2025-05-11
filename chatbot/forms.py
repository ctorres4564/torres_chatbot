# chatbot/forms.py
from django import forms

class ChatForm(forms.Form):
    prompt = forms.CharField(
        label="Sua pergunta",
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Digite sua pergunta aqui...'}),
        required=True
    )