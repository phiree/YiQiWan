from django.db import models
from django.contrib.auth.models import User

from model_utils import Choices
from model_utils.fields import SplitField,StatusField,MonitorField

from datetime import  datetime as DateTime
from decimal import Decimal, ROUND_HALF_EVEN

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
    place=models.ForeignKey(Place)
    min_participants=models.IntegerField()
    max_participants=models.IntegerField()
    start_time=models.DateTimeField()
    end_time=models.DateTimeField()
    #founder close the activity.
    close_time=MonitorField(monitor='status',when='Closed')
    participate_deadline=models.DateTimeField()
    activity_type=models.CharField(max_length=100)
    #can ensure the cost
    total_cost_expected=models.IntegerField()
    #can't ensure
    total_cost_min_expected=models.IntegerField()
    total_cost_max_expected=models.IntegerField()
    total_cost_actual=models.DecimalField(max_digits=9,decimal_places=1)
    participants=models.ManyToManyField(User,related_name='activity_participants')
    STATUS=Choices('Open','Progressing','Over','Closed')
    status=StatusField(STATUS)

    @property
    def balance_required(self):
        participant_amount=self.participants.count() if self.participants.count()>=self.min_participants else self.min_participants
        total_price=self.total_cost_expected if self.total_cost_expected else self.total_cost_max_expected
        return total_price/participant_amount

    def add_participant(self,participant):
        #check total participants
        if participant==self.founder:
            return (False,'no need , you are the founder')
        if self.participants.filter(id=participant.id):
            return (False,'already in')
        if self.status!='Open':
            return (False,'it is not open')
        #check time
        if DateTime.now()>self.participate_deadline:
            return (False,'too late')
        #check person amount
        if self.participants.count()>=self.max_participants:
            return (False,'full')

        self.participants.add(participant)
        #check money

        if participant.balance.amount<self.balance_required:
            return (False,'not enought money')

        return (True,'')

class Financial_Statement(models.Model):
    """
    借贷表
    """
    #这两种借贷方 可以从activity中提取出来..
    #participant_balances=models.ForeignKey(User_Balance)
    #founder_balance=models.OneToOneField(User)
    #财务事件
    activity=models.ForeignKey(Activity)
    #支出(活动参与者)为负,收入(活动建立者,系统利润)为正
    amount_for_participants=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='参与者支付金额')
    amount_for_founder=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='创建者收取金额')
    amount_for_founder_profit=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='创建者盈利')
    amount_for_system_profit=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='系统盈利')

    #待完成(预扣,预收,预盈利)
    STATUS=Choices('Pendding','Complete')
    status=StatusField(STATUS)
    #发生时间
    occur_time=models.DateTimeField()
    #结束时间
    complete_time=models.DateTimeField(null=True)
    #账户余额

class User_Balance(models.Model):
    user=models.ForeignKey(User)
    amount=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='可用余额')
    amount_withhold=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='预付总额')
    amount_advance_receive=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='预收总额')
User.balance=property(lambda u:User_Balance.objects.get_or_create(user=u)[0])


class System_Balance(models.Model):
    """
    系统账户余额
    """
    amount=models.DecimalField(max_digits=9,decimal_places=1)
    amount_advance_receive=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='预收总额')
#结算策略,
import math
class Checkout_Strategy(models.Model):
    activity=models.OneToOneField(Activity)
    #创建者分红比例
    founder_profit_percent=models.DecimalField(max_digits=2,decimal_places=1)
    is_founder_free=models.BooleanField(default=False)
    def get_amount_occur(self):
        return self.activity.total_cost_actual
        pass

    def checkout(self):
        #活动需要收取的原始费用(每个用户支付额未求整之前)
        total_amount_occur=self.get_amount_occur()
        participant_amount=self.activity.participants.count()
        if not self.is_founder_free:
            participant_amount+=1
        real_cost_each=math.ceil(total_amount_occur/participant_amount)
        #每个参与者的aa费用求整之后的总费用
        tatal_amount_need_charge=real_cost_each*participant_amount

        amount_profit=tatal_amount_need_charge-self.activity.total_cost_actual
        amount_profit_founder=Decimal(amount_profit*self.founder_profit_percent).quantize(Decimal('.1'), rounding=ROUND_HALF_EVEN)
        amount_profit_system=amount_profit-amount_profit_founder

        #借贷表
        Financial_Statement.objects.create(
            activity=self.activity,
            amount_for_participants= tatal_amount_need_charge,#参与者(包括创建者应该支付的费用)
            amount_for_founder=self.activity.total_cost_actual,#活动参与者收取的费用(用于线下支付给商家)
            amount_for_founder_profit=amount_profit_founder,
            amount_for_system_profit=amount_profit_system,
            occur_time=DateTime.now()
        )

class Checkout_Strategy_Fix_Charge(Checkout_Strategy):
    fix_charge=models.DecimalField(max_digits=9,decimal_places=1)
    def get_amount_occur(self):
        return self.activity.total_cost_actual+self.fix_charge









