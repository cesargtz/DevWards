from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm): #Genera un formulario a partir de un modelo

    class Meta:
        model = User
        fields = ('username', 'email', 'password') #los campos que se mostraran en pantalla
        widgets = {
            'username': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Username'
            }),
            'email': forms.TextInput(attrs={
                'type': 'text',
                'placeholder': 'Email'
            }),
            'password': forms.TextInput(attrs={
                'type': 'password',
                'placeholder': 'password'
            })
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'type': 'text',
        'placeholder': 'Usuario'
    }))
    password = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'type': 'password',
        'placeholder': 'Contraseña'
    }))

    def clean(self): #con esta funcion envia los json del formulario
        user_found = User.objects.filter(username = self.cleaned_data['username']).exists() #el filter trae una lista de objectos pero si lo combina con el existi solo retorna un true o false
        if not user_found:
            self.add_error('username','Usuario y/o Contraseña no encontrados') #mandas un mensaje de error a la caja de texto
        else:
            user = User.objects.get(username = self.cleaned_data['username']) # El Get trae solo un objeto
            if not user.check_password(self.cleaned_data['password']):
                self.add_error('password','Contraseña Incorrecta')
