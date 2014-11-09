from django.test import TestCase
from unittest.mock import  Mock,MagicMock
from web.models import Activity,User,User_Balance,Place,Checkout_Strategy,Financial_Statement
from datetime import   datetime as DateTime,timedelta
# Create your tests here.
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
class activity_test(TestCase):
    def setUp(self):
        users=mommy .make("User",_quantity=6)
        self.user1=users[0]
        self.user2=users[1]
        self.user3=users[2]
        self.user4=users[3]
        self.user5=users[4]
        self.user6=users[5]
        self.activity1=mommy.make("Activity",
                                  description='desc',
            founder=self.user1,
            min_participants=2,
            max_participants=4,
            participate_deadline=DateTime.now()+timedelta(hours=1),
            total_cost_expected=100,
            total_cost_min_expected=50,
            total_cost_max_expected=120,
            total_cost_actual=100
        )
        self.user_balance=mommy.make("User_Balance",user=self.user1, amount=10)
    def test_add_participant_already_in(self):

        #founder no need join
        result1=self.activity1.add_participant(self.user1)
        self.assertFalse(result1[0],result1[1])
        #repeat join
        self.activity1.add_participant(self.user2)
        result2=self.activity1.add_participant(self.user2)
        self.assertFalse(result2[0],result2[1])

    def test_add_participant_when_full(self):
        self.activity1.total_cost_expected=-1
        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        result=self.activity1.add_participant(self.user5)
        self.assertTrue(result[0],msg=result[1])
        result2=self.activity1.add_participant(self.user6)
        self.assertFalse(result2[0],result2[1])

    def test_add_participant_after_deadline(self):
        self.activity1.participate_deadline=DateTime.now()+ timedelta(hours=-1)
        self.activity1.max_participants=3
        result=self.activity1.add_participant(self.user1)
        self.assertFalse(result[0], msg=result[1])

    def test_add_participant_check_balance(self):
        #ensure other conditions
        self.activity1.participate_deadline=DateTime.now()+ timedelta(hours=1)
        #not enough money
        self.user2.balance.amount=10
        self.user2.balance.save()
        self.assertFalse(self.activity1.add_participant(self.user2)[0])
        #enougn money
        user_balance3=mommy.make("User_Balance",user=self.user3,amount=50)
        result=self.activity1.add_participant(self.user3)
        self.assertTrue(result[0],msg=result[1])

    def test_check_out_founder_not_free(self):

        self.user1.balance.amount=0
        #self.user1.
        user_balance2=mommy.make("User_Balance",user=self.user2,amount=50)
        user_balance3=mommy.make("User_Balance",user=self.user3,amount=50)
        user_balance4=mommy.make("User_Balance",user=self.user4,amount=50)

        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        checkout_stratege=mommy.make('Checkout_Strategy',activity=self.activity1,founder_profit_percent=0.2)
        checkout_stratege.checkout()
        fs=Financial_Statement.objects.all()[0]
        print(fs.amount_for_participants/(fs.activity.participants.count()+1))
        print(fs.amount_for_participants)
        print(fs.amount_for_founder)
        print(fs.amount_for_founder_profit)
        print(fs.amount_for_system_profit)
        self.assertEqual(0,fs.amount_for_participants
                            -fs.amount_for_founder
                            -fs.amount_for_founder_profit
                            -fs.amount_for_system_profit,
                         'not balance')

    def test_check_out_founder_free(self):
        """
        创建者不需要支付aa费用,仅获取分成.
        """
        self.user1.balance.amount=0
        #self.user1.
        user_balance2=mommy.make("User_Balance",user=self.user2,amount=50)
        user_balance3=mommy.make("User_Balance",user=self.user3,amount=50)
        user_balance4=mommy.make("User_Balance",user=self.user4,amount=50)

        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        checkout_stratege=mommy.make('Checkout_Strategy',activity=self.activity1
                                     ,is_founder_free=True, founder_profit_percent=0.2)
        checkout_stratege.checkout()
        fs=Financial_Statement.objects.all()[0]
        print(fs.amount_for_participants/fs.activity.participants.count())
        print(fs.amount_for_participants)
        print(fs.amount_for_founder)
        print(fs.amount_for_founder_profit)
        print(fs.amount_for_system_profit)
        self.assertEqual(0,fs.amount_for_participants
                            -fs.amount_for_founder
                            -fs.amount_for_founder_profit
                            -fs.amount_for_system_profit,
                         'not balance')

    def test_check_out_fix_charge(self):
        """系统收取固定费用"""
        self.user1.balance.amount=0
        #self.user1.
        user_balance2=mommy.make("User_Balance",user=self.user2,amount=50)
        user_balance3=mommy.make("User_Balance",user=self.user3,amount=50)
        user_balance4=mommy.make("User_Balance",user=self.user4,amount=50)

        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        checkout_stratege=mommy.make('Checkout_Strategy_Fix_Charge',fix_charge=5, activity=self.activity1
                                     ,is_founder_free=True, founder_profit_percent=0.2)
        checkout_stratege.checkout()
        fs=Financial_Statement.objects.all()[0]
        print(fs.amount_for_participants/fs.activity.participants.count())
        print(fs.amount_for_participants)
        print(fs.amount_for_founder)
        print(fs.amount_for_founder_profit)
        print(fs.amount_for_system_profit)
        self.assertEqual(0,fs.amount_for_participants
                            -fs.amount_for_founder
                            -fs.amount_for_founder_profit
                            -fs.amount_for_system_profit,
                         'not balance')










