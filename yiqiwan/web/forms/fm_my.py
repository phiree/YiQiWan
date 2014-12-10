# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from django.forms import forms, ModelForm,HiddenInput, TextInput,DateTimeInput,Form,CharField,DecimalField,IntegerField
from ..models import Activity,User2,Interest
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.models import ModelMultipleChoiceField
class fm_charge_activity(Form):
    charge_user_id=IntegerField(widget=HiddenInput)
    amount=DecimalField(max_digits=4,decimal_places=1)

    pass
class CustomSelectMultiple(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s" %(obj.name)
class fm_interest(ModelForm):
    interests = CustomSelectMultiple(widget=CheckboxSelectMultiple, queryset=Interest.objects.all(),required=False )
    class Meta:
        model=User2
        fields=['interests',]
        #widgets = {"interests":CheckboxSelectMultiple(),}
