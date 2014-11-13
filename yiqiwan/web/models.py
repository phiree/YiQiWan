from django.db import models
from django.contrib.auth.models import User

from model_utils import Choices
from model_utils.fields import SplitField,StatusField,MonitorField

#from datetime import  datetime as DateTime
from django.utils import timezone as DateTime
#from django.utils.timezone import datetime as DateTime
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
    def __str__(self):
        return self.address

class Activity(models.Model):
    """
    活动的定义.
    """
    founder=models.ForeignKey(User,related_name='activity_founder',verbose_name='创建者',blank=True,
                              null=True, help_text='创建者')
    name=models.CharField(max_length=300,null=True,blank=True)
    description=SplitField(max_length=8000,null=True,blank=True)
    place=models.ForeignKey(Place)
    min_participants=models.IntegerField()
    max_participants=models.IntegerField()
    start_time=models.DateTimeField()
    end_time=models.DateTimeField()
    #other_user close the activity.
    close_time=MonitorField(monitor='status',null=True,blank=True, when='Closed')
    participate_deadline=models.DateTimeField()
    activity_type=models.CharField(max_length=100,null=True,blank=True)
    #can ensure the cost
    total_cost_expected=models.IntegerField()
    #can't ensure
    total_cost_max_expected=models.IntegerField()
    total_cost_actual=models.DecimalField(null=True,blank=True, max_digits=9,decimal_places=1)
    participants=models.ManyToManyField(User,related_name='activity_participants',null=True,blank=True)
    STATUS=Choices('Open','Progressing','Over','Closed')
    status=StatusField(STATUS,default='Open',blank=True)
    create_time=models.DateTimeField(auto_now=True)
    @property
    def balance_required(self):
        participant_amount=self.participants.count() if self.participants.count()>=self.min_participants else self.min_participants
        total_price=self.total_cost_expected if self.total_cost_expected else self.total_cost_max_expected
        return Decimal(total_price/participant_amount)
    #增加參與者
    def add_participant(self,participant):
        #check total participants
        msg='join successfully'
        if participant==self.founder:
            return (False,'no need , you are the other_user')
        if self.participants.filter(id=participant.id):
            return (False,'already in')
        if self.status!='Open':
            return (False,'it is not open')
        #check time
        if DateTime.now()>self.participate_deadline:
            return (False,'too late')
        #check person amount_debet
        if self.participants.count()>=self.max_participants:
           return (False,'full')

        if participant.user_balance.amount_capital_debt<self.balance_required and\
           participant.user_user_balance_owner.filter(other_user=self.founder)[0].amount_capital_debt<self.balance_required:
            msg='waring:not enough money to pay the amount_debet online,please pay cash to the other_user and ask him to add balance to your account.'
             #预扣款应该支付给 和创建者相关的离线账号.

        #todo 事务处理
        self.participants.add(participant)
        #凍結預付款 所有用戶都一樣. 该过程只影响离线账户
        balance_flow=Balance_Flow.objects.create(flow_type=flow_type_choice[0][0]
                    #todo ensure the account exits only one
                    #应收应付 已经
                    ,from_account=User_User_Balance.objects.filter(owner=participant,other_user=self.founder)[0]
                    ,to_account=None
                    ,amount=self.balance_required
                    ,occur_time=DateTime.now()
                    ,activity=self
                    ,applied=False
                    )
        #todo 事务处理
        balance_flow.apply_flow()
        balance_flow.applied=True
        balance_flow.save()
        Activity_Timeline.objects.create(user=participant,activity=self,occur_time=DateTime.now(),direction='J')
        return (True,msg)
    #移除參與者.
    def remote_participant(self):
        pass
    def __str__(self):
        return self.name+"_"+self.activity_type+"_"+self.place.name
#活動的時間線
class Activity_Timeline(models.Model):
    """記錄用戶的 參與/離去時間"""
    user=models.ForeignKey(User)
    activity=models.ForeignKey(Activity)
    occur_time=models.DateTimeField(default=DateTime.now())
    direction=models.CharField(choices=(('L','leave'),('J','join')),max_length=10)

#营业财务表
class Financial_Statement(models.Model):

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

#拥护充值记录: 用户与用户,拥护与平台.
class Recharge(models.Model):
    occur_time=models.DateTimeField()
    from_balance=models.ForeignKey('User_Balance',related_name='recharge_from')
    to_balance=models.ForeignKey('User_Balance',related_name='recharge_to')
    amount=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='金额')
    pass

class Base_Balance(models.Model):
    #todo 该meta是为了防止它实例化, 为何不能做Foreign key?..
    class Meta:
        pass
        #abstract=True
    amount_capital_debt=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='资产/负债')#资产和负债可以合并
    amount_profit_loss=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='利润/亏损')#利润和亏损也合并 负数则为亏损
    amount_payables_receivables=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='应收/应付')#预款总额 应收和应付也合并 负数则为亏损
    #实际余额
    @property
    def balance_actual(self):
        return self.amount_capital_debt+self.amount_profit_loss
    #包含预付预收的
    def balance_expected(self):
        return self.balance_actual+self.amount_payables_receivables
#在线账户总额 每个用户只能有一个在线账户
class User_Balance(Base_Balance):
    owner=models.OneToOneField(User)

#流水帐. 类型,1)参与活动(预扣款)2)活动结帐(实际扣款) 3)为线上账户充值 4)从线上账户提现 5)创建者为参与者离线账户充值 6)用户从离线账户取现(现场取回现金)
flow_type_choice=(('activity_pre_checkout','活动预结帐'),
                    ('activity_checkout','活动结帐'),
                    ('activity_checkout','活动取消'),

                    ('recharge_offline','在线充值'),# 用户充值给系统
                    ('withdraw_offline','在线提现'),# 用户从系统体现
                     ('recharge_online','离线充值'),#用户之间的余额转移,如 参与者交款给 创建者
                    ('withdraw_online','离线提现'),#                     参与者要回现金
)#同上
#借贷流水
class Balance_Flow(models.Model):
    flow_type=models.CharField(choices=flow_type_choice,max_length=50)
    from_account=models.ForeignKey(Base_Balance,related_name='balance_flow_from')
    to_account=models.ForeignKey(Base_Balance,related_name='balance_flow_to',null=True,blank=True)
    amount=models.DecimalField(default=0,max_digits=6,decimal_places=1,help_text='金额')
    occur_time=models.DateTimeField(auto_now=True,default=DateTime.now())
    activity=models.ForeignKey(Activity,null=True,blank=True)
    applied=models.BooleanField(default=False)

    def apply_flow(self):
        """根据流水,更新各个账户
        离线账户的一笔流水只需要记一次. 因为离线账户已经包含了贷方(比如活动预结帐里的创建者)
        """
        if self.applied:
            return (False,'Error.flow had been checked, cannot apply again ')

        if self.flow_type==flow_type_choice[0][0]:
            #from_account 是参与者账户,to 是创建者账户
            self.from_account.amount_payables_receivables+=-1*self.amount #应付增加 减法
            self.from_account.amount_capital_debt+=-1*self.amount#资产负债增加,减法
            #self.to_account.amount_payables_receivables+=self.amount #应收 增加

        elif self.flow_type==flow_type_choice[1][0]:
            self.from_account.amount_payables_receivables+=self.amount #应付减少 加法.
            #self.to_account.amount_payables_receivables-=self.amount #应收减少
            #self.to_account.amount_capital_debt+=self.amount #资产增加

        elif self.flow_type== flow_type_choice[2][0]:
            self.from_account.amount_payables_receivables+=self.amount#应付减少
            self.from_account.amount_capital_debt+=self.amount#资产增加
            #self.to_acount.amount_payables_receivables-=self.amount #应收减少

        elif self.flow_type== flow_type_choice[3][0]: #在线充值
            self.from_account.amount_capital_debt+=self.amount
            self.to_account.amount_capital_debt-=self.amount

        elif self.flow_type== flow_type_choice[4][0]:#在线提现
            self.from_account.amount_capital_debt-=self.amount
            self.to_account.amount_capital_debt+=self.amount
        elif self.flow_type== flow_type_choice[5][0]:#离线充值
            self.from_account.amount_capital_debt+=self.amount
        elif self.flow_type==flow_type_choice[6][0]:#离线充值
            self.from_account.amount_capital_debt-=self.amount

        #todo 事务处理
        self.from_account.save()
        if self.to_account:
            self.to_account.save()
        return True

#用户之间的账户:离线账户
class User_User_Balance(Base_Balance):
    owner=models.ForeignKey(User,related_name='user_user_balance_owner')
    other_user=models.ForeignKey(User,related_name='user_user_balance_other_user')

#平台帐户
class System_Balance(Base_Balance):
    pass
#结算策略.
import math
class Checkout_Strategy(models.Model):

    activity=models.OneToOneField(Activity)
    #创建者分红比例
    founder_profit_percent=models.DecimalField(max_digits=2,decimal_places=1)
    is_founder_free=models.BooleanField(default=False)
    def get_amount_occur(self):
        return self.activity.total_cost_actual
        pass
    #成立条件:参与者在线账户或者对创建者的离线账户余额不能少于aa费用.否则提醒创建者让用户交钱.

    def checkout(self):
        #活动需要收取的原始费用(参与者支付额未求整之前)
        total_amount_occur=self.get_amount_occur()
        participant_amount=self.activity.participants.count()
        if not self.is_founder_free:
            participant_amount+=1
        real_cost_each=math.ceil(total_amount_occur/participant_amount)
        #确认参与者的两个账户至少有一个的余额能够支付本次活动.
        #或者,允许参加,只不过应付账款增加. 需要参与者线下督促用户付现金.
        #每个参与者的aa费用求整之后的总费用
        tatal_amount_need_charge=real_cost_each*participant_amount
        #利润分要分为两部分,线上支付的aa费用产生的利润, 线下用户直接付给创建者的费用.
        #第一部分的利润由平台和创建者分享, 后一部分由创建者独享.
        amount_profit=tatal_amount_need_charge-self.activity.total_cost_actual
        #如果利润小于0,则创建者承担全部亏损
        if amount_profit<0:
            self.founder_profit_percent=1

        amount_profit_founder=Decimal(amount_profit*self.founder_profit_percent).quantize(Decimal('.1'), rounding=ROUND_HALF_EVEN)
        amount_profit_system=amount_profit-amount_profit_founder

        #更新账户:
        for participant in self.activity.participants.all():
            #优先使用在线账户支付.如果不足,再使用离线账户
            balance_flow=Balance_Flow(flow_type=flow_type_choice[1][0]
                    ,from_account=participant.user_balance
                    ,to_account=System_Balance.objects.all()[0] #系统账户只能有一个.
                    ,amount=self.activity.balance_required
                    ,occur_time=DateTime.now()
                    ,activity=self.activity
                    ,applied=False
                    )
            #todo 使用财务期间的方式 减少对流水表的访问,提高性能
            #todo 需要使用事务.
            if participant.user_balance.balance_actual>=real_cost_each:

                pass
            else:
                #离线账户支付
                balance_flow.to_account=None
                balance_flow.from_account=from_account=User_User_Balance.objects.filter(owner=participant,other_user=self.activity.founder)[0]
                pass
            balance_flow.apply_flow()


        #营业收入表
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









