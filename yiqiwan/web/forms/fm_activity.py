# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from django.forms import ModelForm,TextInput,DateTimeInput
from ..models import Activity

class ActivityForm(ModelForm):
    class Meta:
        model=Activity
        exclude=['place']
        widgets = {
            'start_time': TextInput(attrs={'type': 'datetime'}),
            'end_time': TextInput(attrs={'type': 'datetime'}),
            'participate_deadline': TextInput(attrs={'type': 'datetime'}),
        }


