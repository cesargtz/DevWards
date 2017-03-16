from django import forms
from .models import WebSite

class CreateWebsite(forms.ModelForm):

    class Meta:
        model = WebSite
        fields = ('name','url','description','designer','designer_url','twitter','image1','image2','image3')
        widgets = {
            'name': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Nombre'
            }),
            'url': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Url'
            }),
            'description': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Descrición'
            }),
            'designer': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Diseñado Por'
            }),
            'designer_url': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Diseñado Url'
            }),
            'twitter': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Twitter'
            }),
        }
