# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from ..models import User,Activity,Balance_Flow,User_User_Balance
from datetime import datetime as DateTime
from django.db.models import Q
def get_user_balance_flow(user,account_id):
    #todo how to get real account type from this query.
    if account_id:
        flow_list= Balance_Flow.objects.filter(account__id=account_id)
    else:
        flow_list=Balance_Flow.objects.filter(Q(account__owner=user)|Q(account__other_user=user))

    return flow_list