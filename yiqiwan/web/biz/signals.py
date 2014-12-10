# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Financial_Statement
@receiver(post_save, sender=Financial_Statement)
def modify_balance(self):
    cc=1
    pass