__author__ = 'Administrator'
from ..models import User,Activity,User_Account
from datetime import datetime as DateTime
def user_join_activity(user=User,activity=Activity):
    now=DateTime.now()
    #过了某个时间就不能报名
    if now>activity.participate_deadline:
        return (False,'too late')
    current_participants=len(activity.participants)
    if current_participants==activity.max_participant:
        return (False,'no rooms')
    min_pay=activity.total_cost_expected/ ( activity.min_participant if current_participants<=activity.min_participant else current_participants)
    if user.user_acount.balance<min_pay:
        if user.user_acount.balance<activity.total_cost_expected/activity.max_participant:
            return (False,'not enough money')
        else:
            return (False,'not enough money for now. you can take part in when the particapant amount reach '+activity.total_cost_expected/user.user_acount.balance)


