# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from django.forms import ModelForm,TextInput,DateTimeInput,PasswordInput
from ..models import Activity,User2
from django.contrib.auth.models import User

from django.conf import  settings
class RegisterForm(ModelForm):
    class Meta:
        model=User2
        fields=['username','password']
        widgets={
            'password':PasswordInput()
        }



