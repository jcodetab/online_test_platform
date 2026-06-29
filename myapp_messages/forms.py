from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'text']

class FileUploadForm(forms.Form):
    file = forms.FileField()


