__author__ = 'Administrator'
from django.forms import ModelForm,TextInput,DateTimeInput,PasswordInput
from ..models import Activity
from django.contrib.auth.models import User

class RegisterForm(ModelForm):
    class Meta:
        model=User
        fields=['username','password']
        widgets={
            'password':PasswordInput()
        }



