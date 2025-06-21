from django import forms
from .models import DiaryEntry

class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ['title', 'content','photo']

        widgets={
            'title' : forms.TextInput(attrs={'placeholder':'Başlık'}),
            'content':forms.Textarea(attrs={'placeholder' : 'Bugün NE oldu?'}),
        }
