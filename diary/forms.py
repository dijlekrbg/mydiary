from django import forms
from django.contrib.auth.models import User
from .models import DiaryEntry,Photo 

class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ['title', 'content','photo','is_favorite','tags']

        widgets={
            'title' : forms.TextInput(attrs={'placeholder':'Başlık'}),
            'content':forms.Textarea(attrs={'placeholder' : 'Bugün NE oldu?'}),
        }



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class PhotoForm(forms.Form):
    images = forms.FileField(
        required=False,
        label="fotoğraflar")


