from django.db import models
from django.contrib.auth.models import User
from model_utils import Choices
from model_utils.fields import SplitField,StatusField,MonitorField
'''
statium info
'''
class Place(models.Model):
    """
    活动地址的定义
    """
    name=models.CharField(max_length=300)
    address=models.CharField(max_length=300)
    coordinate_x=models.DecimalField(max_digits=9,decimal_places=6)
    coordinate_y=models.DecimalField(max_digits=9,decimal_places=6)
    phone=models.CharField(max_length=200)
    owner=models.ForeignKey(User,null=True,blank=True)
    create_date=models.DateTimeField()
    last_update_time=models.DateTimeField()
    photo=models.ImageField(blank=True,null=True)
    pass


class Activity(models.Model):
    """
    活动的定义.
    """
    founder=models.ForeignKey(User,related_name='activity_founder',help_text='创建者')
    name=models.CharField(max_length=300)
    description=SplitField(max_length=8000)
    stadium=models.ForeignKey(Place)
    min_participant=models.IntegerField()
    max_participant=models.IntegerField()
    start_time=models.DateTimeField()
    end_time=models.DateTimeField()
    #founder close the activity.
    close_time=MonitorField(monitor='status',when='Closed')
    participate_deadline=models.DateTimeField()
    activity_type=models.CharField(max_length=100)
    total_price=models.IntegerField()
    total_price_min=models.IntegerField()
    total_price_max=models.IntegerField()
    participants=models.ManyToManyField(User,related_name='activity_participants')
    STATUS=Choices('Available','Progressing','Over','Closed')
    status=StatusField(STATUS)

class Activity_Checkout(models.Model):
    """
    活动结帐详情
    """
    activity=models.ForeignKey(Activity)
    
    pass

class User_Account(models.Model):
    user=models.OneToOneField(User)
    balance=models.DecimalField(max_digits=6,decimal_places=1)







