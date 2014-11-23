from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User

from model_utils import Choices
from model_utils.fields import SplitField, StatusField, MonitorField

# from datetime import  datetime as DateTime
from django.utils import timezone as DateTime
#from django.utils.timezone import datetime as DateTime
from decimal import Decimal, ROUND_HALF_EVEN
from model_utils.managers import InheritanceManager


class Place(models.Model):
    """
    活动地址的定义
    """
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    coordinate_x = models.DecimalField(max_digits=9, decimal_places=6)
    coordinate_y = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=200)
    owner = models.ForeignKey(User, null=True, blank=True)
    create_date = models.DateTimeField()
    last_update_time = models.DateTimeField()
    photo = models.ImageField(blank=True, null=True)
    pass

    def __str__(self):
        return self.address

class Activity(models.Model):
    """
    活动的定义.
    """
    founder = models.ForeignKey(User, related_name='activity_founder', verbose_name='创建者', blank=True,
                                null=True, help_text='创建者')
    name = models.CharField(max_length=300, null=True, blank=True)
    description =models.CharField(max_length=8000, null=True, blank=True)
    place = models.ForeignKey(Place)
    min_participants = models.IntegerField()
    max_participants = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    #other_user close the activity.
    close_time = MonitorField(monitor='status', null=True, blank=True, when='Closed')
    participate_deadline = models.DateTimeField()
    activity_type = models.CharField(max_length=100, null=True, blank=True)
    #can ensure the cost
    total_cost_expected = models.IntegerField()
    #can't ensure
    total_cost_max_expected = models.IntegerField()
    total_cost_actual = models.DecimalField(null=True, blank=True, max_digits=9, decimal_places=1)
    checkout_strategy=models.ForeignKey('Checkout_Strategy',null=True,blank=True)
    participants = models.ManyToManyField('User2', related_name='activity_participants', null=True, blank=True)
    status_choice = Choices('Open', 'Progressing', 'Over', 'Closed')
    status = models.CharField(max_length=20, choices=status_choice, default='Open', blank=True)
    create_time = models.DateTimeField(auto_now=True)

    def get_each_pay_preview(self):
        total_cost_max= self.total_cost_max_expected if self.total_cost_max_expected else self.total_cost_expected
        total_cost_min=self.total_cost_expected if self.total_cost_expected else self.total_cost_max_expected
        extra_charge_min=self.checkout_strategy.get_charge_amount(total_cost_min)
        extra_charge_max=self.checkout_strategy.get_charge_amount(total_cost_max)
        total_amount_occur_max = total_cost_max+extra_charge_max
        total_amount_occur_min = total_cost_min+extra_charge_min
        participant_amount = self.participants.count()
        if not self.checkout_strategy.is_founder_free:
            participant_amount += 1
        return  math.ceil(Decimal(total_amount_occur_min/participant_amount)), math.ceil(Decimal(total_amount_occur_max/participant_amount))

    def get_each_pay(self,actual_cost):
        total_amount_occur = actual_cost+self.checkout_strategy.get_charge_amount(actual_cost)
        participant_amount = self.participants.count()
        if not self.checkout_strategy.is_founder_free:
            participant_amount += 1
        return math.ceil(Decimal(total_amount_occur/participant_amount))
    #结帐
    def checkout(self,actual_cost):
        #活动需要收取的原始费用(参与者支付额未求整之前)
        self.total_cost_actual=actual_cost
        self.save()
        real_cost_each = self.get_each_pay(actual_cost)
        #确认参与者的两个账户至少有一个的余额能够支付本次活动.
        #或者,允许参加,只不过应付账款增加. 需要参与者线下督促用户付现金.
        #每个参与者的aa费用求整之后的总费用
        total_amount_need_charge = real_cost_each * self.participants.count()
        #利润分要分为两部分,线上支付的aa费用产生的利润, 线下用户直接付给创建者的费用.
        #第一部分的利润由平台和创建者分享, 后一部分由创建者独享.
        amount_profit = total_amount_need_charge - actual_cost
        #如果利润小于0,则创建者承担全部亏损
        if amount_profit < 0:
            self.checkout_strategy.founder_profit_percent = 1

        amount_profit_founder = Decimal(amount_profit * self.checkout_strategy.founder_profit_percent).quantize(Decimal('.1'),
                                                                                              rounding=ROUND_HALF_EVEN)
        amount_profit_system = amount_profit - amount_profit_founder

        #更新账户:
        for participant in self.participants.all():
            #优先使用在线账户支付.如果不足,再使用离线账户. 剩余账户为负 由 创建者找用户解决.

            participant_checkout(participant=participant
                                 , activity=self, amount=real_cost_each
                                 , flow_type=flow_type_choice[1][0])

        #营业收入表
        Financial_Statement.objects.create(
            activity=self,
            amount_for_participants=total_amount_need_charge,  #参与者(包括创建者应该支付的费用)
            amount_for_founder=self.total_cost_actual,  #活动参与者收取的费用(用于线下支付给商家)
            amount_for_founder_profit=amount_profit_founder,
            amount_for_system_profit=amount_profit_system,
            occur_time=DateTime.now()
        )

    @property
    def balance_required(self):
        total_price = self.total_cost_expected if self.total_cost_expected else self.total_cost_max_expected

        return math.ceil(Decimal(total_price / self.min_participants))

    #增加參與者
    def add_participant(self, participant):
        #check total participants
        msg = 'join successfully'
        if participant == self.founder:
            return (False, 'no need , you are the other_user')
        if self.participants.filter(id=participant.id):
            return (False, 'already in')
        if self.status != 'Open':
            return (False, 'it is not open')
        #check time
        if DateTime.now() > self.participate_deadline:
            return (False, 'too late')
        #check person amount_debet
        max_participants = self.max_participants if self.max_participants else self.min_participants
        if self.participants.count() >= max_participants:
            return (False, 'full')
        offline_balance,created=User_User_Balance.objects.get_or_create(owner=participant,other_user=self.founder)
        if participant.user_balance.amount_capital_debt < self.balance_required and \
                        offline_balance.amount_capital_debt < self.balance_required:
            msg = 'waring:not enough money to pay the amount_debet online,please pay cash to the other_user and ask him to add balance to your account.'
            #预扣款应该支付给 和创建者相关的离线账号.

        #todo 事务处理
        self.participants.add(participant)
        #凍結預付款 所有用戶都一樣. 该过程只影响离线账户
        #如果用户的在线账户本来就有余额,那么优先使用在线账户.
        #离线账户
        participant_checkout(participant=participant, activity=self, amount=self.balance_required,
                             flow_type=flow_type_choice[0][0])
        Activity_Timeline.objects.create(user=participant, activity=self, occur_time=DateTime.now(), direction='J')
        return (True, msg)

    #移除參與者.
    def remote_participant(self):
        pass

    def __str__(self):
        return self.name + "_" + self.activity_type + "_" + self.place.name
    #自动套用strategy
    def save(self, *args, **kwargs):
        try:
            #todo 为 model-utils 的inheritmanager 增加一个  get_or_create_subclass 方法
            strategy= Checkout_Strategy.objects.get_subclass(
                enabled=True
            )
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            strategy= Checkout_Strategy.objects.create(enabled=True)

        self.checkout_strategy=strategy
        super(Activity,self).save(*args,**kwargs)

#活動的時間線
class Activity_Timeline(models.Model):
    """記錄用戶的 參與/離去時間"""
    user = models.ForeignKey(User)
    activity = models.ForeignKey(Activity)
    occur_time = models.DateTimeField(default=DateTime.now())
    direction = models.CharField(choices=(('L', 'leave'), ('J', 'join')), max_length=10)


#营业财务表
class Financial_Statement(models.Model):
    #这两种借贷方 可以从activity中提取出来..
    #participant_balances=models.ForeignKey(User_Balance)
    #founder_balance=models.OneToOneField(User)
    #财务事件
    activity = models.ForeignKey(Activity)
    #支出(活动参与者)为负,收入(活动建立者,系统利润)为正
    amount_for_participants = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='参与者支付金额')
    amount_for_founder = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='创建者收取金额')
    amount_for_founder_profit = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='创建者盈利')
    amount_for_system_profit = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='系统盈利')

    #待完成(预扣,预收,预盈利)
    STATUS = Choices('Pendding', 'Complete')
    status = StatusField(STATUS)
    #发生时间
    occur_time = models.DateTimeField()
    #结束时间
    complete_time = models.DateTimeField(null=True)


#拥护充值记录: 用户与用户,拥护与平台.
class Recharge(models.Model):
    occur_time = models.DateTimeField()
    from_balance = models.ForeignKey('User_Balance', related_name='recharge_from')
    to_balance = models.ForeignKey('User_Balance', related_name='recharge_to')
    amount = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='金额')
    pass


class Base_Balance(models.Model):
    #todo 该meta是为了防止它实例化, 为何不能做Foreign key?..
    class Meta:
        pass
        #abstract=True

    amount_capital_debt = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='资产/负债')  #资产和负债可以合并
    amount_profit_loss = models.DecimalField(default=0, max_digits=6, decimal_places=1,
                                             help_text='利润/亏损')  #利润和亏损也合并 负数则为亏损
    amount_payables_receivables = models.DecimalField(default=0, max_digits=6, decimal_places=1,
                                                      help_text='应收/应付')  #预款总额 应收和应付也合并 负数则为亏损
    #实际余额
    @property
    def balance_actual(self):
        return self.amount_capital_debt + self.amount_profit_loss

    #包含预付预收的
    def balance_expected(self):
        return self.balance_actual + self.amount_payables_receivables

#扩展的user
class User2(User):
    user=models.OneToOneField(User)
    def get_user_user_balance(self,other_user):
        return User_User_Balance.objects.get_or_create(owner=self.user,other_user=other_user)
#在线账户总额 每个用户只能有一个在线账户
class User_Balance(Base_Balance):
    owner = models.OneToOneField(User2)
User2.user_balance=property(lambda u:User_Balance.objects.get_or_create(owner=u)[0])


#用户之间的账户:离线账户
class User_User_Balance(Base_Balance):
    owner = models.ForeignKey(User2, related_name='user_user_balance_owner')
    other_user = models.ForeignKey(User2, related_name='user_user_balance_other_user')

#系统账户
class System_Balance(Base_Balance):
    pass

#流水帐. 类型,1)参与活动(预扣款)2)活动结帐(实际扣款) 3)为线上账户充值 4)从线上账户提现 5)创建者为参与者离线账户充值 6)用户从离线账户取现(现场取回现金)
flow_type_choice = (('activity_pre_checkout', '活动预结帐'),
                    ('activity_checkout', '活动结帐'),
                    ('activity_checkout', '活动取消'),

                    ('recharge_offline', '在线充值'),  # 用户充值给系统
                    ('withdraw_offline', '在线提现'),  # 用户从系统体现
                    ('recharge_online', '离线充值'),  #用户之间的余额转移,如 参与者交款给 创建者
                    ('withdraw_online', '离线提现'),  #                     参与者要回现金
)  #同上
#借贷流水,
class Balance_Flow(models.Model):
    flow_type = models.CharField(choices=flow_type_choice, max_length=50)
    account_from = models.ForeignKey(Base_Balance, related_name='balance_flow_from')
    #account 收支平衡 不需要 to-account 因为流水双方已经在同一个account,面了
    #update 同一比收支需要分别记录在多个不同的账户里
    account_to=models.ForeignKey(Base_Balance,related_name='balance_flow_to',null=True,blank=True)
    amount = models.DecimalField(default=0, max_digits=6, decimal_places=1, help_text='金额')
    occur_time = models.DateTimeField(auto_now=True, default=DateTime.now())
    activity = models.ForeignKey(Activity, null=True, blank=True)
    applied = models.BooleanField(default=False)

    def apply_flow(self):
        """根据流水,更新各个账户
        离线账户的一笔流水只需要记一次. 因为离线账户已经包含了贷方(比如活动预结帐里的创建者)
        """
        if self.applied:
            return (False, 'Error.flow had been checked, cannot apply again ')

        #加入活动 预扣款
        if self.flow_type == flow_type_choice[0][0]:
            #
            self.account_from.amount_payables_receivables += self.amount  #应付增加 减法
            self.account.amount_capital_debt -= self.amount  #资产负债增加,减法
            self.account_to.amount_payables_receivables+=self.amount #应收 增加

        #实际扣款 清空应付款,而且清空的金额等于预扣的款项,不是加入时的 balance_required
        #amount 值 由来源负责计算, 如果是负数 这表明是 返还 预付款.
        elif self.flow_type == flow_type_choice[1][0]:

            #不能这样清空应付款
            self.account_from.amount_payables_receivables -=self.amount  #清空应付款
            #恢复预扣款
            self.account_from.amount_capital_debt -= self.amount
            #减除实际扣款
            self.account_to.amount_payables_receivables-=self.amount #应收减少
            self.account_to.amount_capital_debt+=self.amount #资产增加
        #活动取消
        elif self.flow_type == flow_type_choice[2][0]:
            self.account_from.amount_payables_receivables -=self.amount  #应付减少
            self.account_from.amount_capital_debt += self.amount  #资产增加
            self.acount_to.amount_payables_receivables-=self.amount #应收减少

        elif self.flow_type == flow_type_choice[3][0]:  #在线充值
            self.account.amount_capital_debt += self.amount
            self.to_account.amount_capital_debt -= self.amount

        elif self.flow_type == flow_type_choice[4][0]:  #在线提现
            self.account.amount_capital_debt -= self.amount
            self.to_account.amount_capital_debt += self.amount
        elif self.flow_type == flow_type_choice[5][0]:  #离线充值
            self.account.amount_capital_debt += self.amount
        elif self.flow_type == flow_type_choice[6][0]:  #离线充值
            self.account.amount_capital_debt -= self.amount

        #todo 事务处理
        self.account.save()

        return True


def participant_checkout(participant, activity, amount, flow_type):

    balance_online = participant.user_balance
    balance_offline = participant.user_user_balance_owner.filter(other_user=activity.founder)[0]
    #实际付款
    if flow_type == flow_type_choice[1][0]:
        balance_online_pre_check,balance_offline_pre_check = None,None
        pre_check_flow_list = Balance_Flow.objects.filter(activity=activity, flow_type=flow_type_choice[0][0])
        #用户的预付款
        pre_check_flow_online_list = pre_check_flow_list.filter(account=balance_online)
        pre_check_flow_offline_list = pre_check_flow_list.filter(account=balance_offline)
        #差价
        actual_diff_amount = amount - activity.balance_required
        if pre_check_flow_online_list.count() == 1:
            pre_check_flow_online = pre_check_flow_online_list[0]
            balance_online_pre_check = pre_check_flow_online.amount
        elif pre_check_flow_online_list.count() > 1:
            raise ('pre_check_flow_online_list.count')
        if pre_check_flow_offline_list.count() == 1:
            pre_check_flow_offline = pre_check_flow_offline_list[0]
            balance_offline_pre_check = pre_check_flow_offline.amount
        elif pre_check_flow_online_list.count() > 1:
            raise ('pre_check_flow_online_list.count')
        #先返回预扣款:模仿实际收款 只不过金额是负数
        if  balance_online_pre_check !=None  :
            balance_flow=Balance_Flow.objects.create(flow_type=flow_type
                        #todo ensure the account exits only one
                        #应收应付 已经
                        ,account=balance_online
                        ,amount=balance_online_pre_check*-1
                        ,occur_time=DateTime.now()
                        ,activity=activity
                        ,applied=False
                        )
            #todo 事务处理
            balance_flow.apply_flow()
            balance_flow.applied=True
            balance_flow.save()

         #在线账户支付后的余额
        if balance_offline_pre_check!=None :

            balance_flow_offline=Balance_Flow.objects.create(flow_type=flow_type
                        #todo ensure the account exits only one
                        #应收应付 已经
                        ,account=balance_offline
                        ,amount=balance_offline_pre_check*-1
                        ,occur_time=DateTime.now()
                        ,activity=activity
                        ,applied=False
                        )
            #todo 事务处理
            balance_flow_offline.apply_flow()
            balance_flow_offline.applied=True
            balance_flow_offline.save()

    pay_amount_online = amount if balance_online.amount_capital_debt >= amount \
        else balance_online.amount_capital_debt
    pay_amount_offline = amount - pay_amount_online


    if    pay_amount_online!=0:
            balance_flow=Balance_Flow.objects.create(flow_type=flow_type
                        #todo ensure the account exits only one
                        #应收应付 已经
                        ,account=balance_online
                        ,amount=pay_amount_online
                        ,occur_time=DateTime.now()
                        ,activity=activity
                        ,applied=False
                        )
            #todo 事务处理
            balance_flow.apply_flow()
            balance_flow.applied=True
            balance_flow.save()

         #在线账户支付后的余额
    if   pay_amount_offline!=0:

        balance_flow_offline=Balance_Flow.objects.create(flow_type=flow_type
                    #todo ensure the account exits only one
                    #应收应付 已经
                    ,account=balance_offline
                    ,amount=pay_amount_offline
                    ,occur_time=DateTime.now()
                    ,activity=activity
                    ,applied=False
                    )
        #todo 事务处理
        balance_flow_offline.apply_flow()
        balance_flow_offline.applied=True
        balance_flow_offline.save()



import math


class Checkout_Strategy(models.Model):
    """结帐策略:"""
    #创建者分红比例
    objects = InheritanceManager()
    founder_profit_percent = models.DecimalField(default=0.2, max_digits=2, decimal_places=1)
    #创建者是否免单
    is_founder_free = models.BooleanField(default=False)
    last_update_time=models.DateTimeField(auto_now=True, default=DateTime.now())
    #todo:ensure there is only one suitable strategy for certain condition.
    #目前还没有其他条件
    enabled=models.BooleanField(default=False)
    # 向上取整前产生的额外费用.
    def get_charge_amount(self,any):
        return 0
        pass

        real_cost_each = math.ceil(total_amount_occur / participant_amount)
    #成立条件:参与者在线账户或者对创建者的离线账户余额不能少于aa费用.否则提醒创建者让用户交钱.

#固定费用
class Checkout_Strategy_Fix_Charge(Checkout_Strategy):
    fix_charge = models.DecimalField(max_digits=9, decimal_places=1)
    def get_charge_amount(self,any):
        return  self.fix_charge

#总额的比例 前期是否设定为10%?
class Checkout_Strategy_Percent_Charge(Checkout_Strategy):
    percent_charge = models.DecimalField(max_digits=3, decimal_places=2)
    max_charge= models.IntegerField()
    def get_charge_amount(self,total_cost_actual):
        charge= total_cost_actual*self.percent_charge
        charge=charge if charge<=self.max_charge else self.max_charge
        return  charge

#多种策略可以选择

#如何决定每个活动的 结帐策略?







