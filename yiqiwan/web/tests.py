from django.test import TestCase
from unittest.mock import  Mock,MagicMock
from web.models import Activity,User,User_Balance,User_User_Balance, Place,Checkout_Strategy,Financial_Statement,Checkout_Strategy_Fix_Charge
from datetime import   timedelta
from django.utils import timezone as DateTime
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
        strategy=mommy.make('Checkout_Strategy_Fix_Charge'
                            ,founder_profit_percent=0.2
                            ,fix_charge=5
                            ,enabled=True
                            )
        self.activity1=mommy.make("Activity",
                                  description='desc',
            founder=self.user1,
            min_participants=2,
            max_participants=4,
            participate_deadline=DateTime.now()+timedelta(hours=1),
            total_cost_expected=100,
            total_cost_max_expected=120,
            total_cost_actual=100
        )


        self.user1_balance=mommy.make("User_Balance",owner=self.user1, amount_capital_debt=10)
        self.user2_balance=mommy.make("User_Balance",owner=self.user2, amount_capital_debt=10)
        self.user3_balance=mommy.make("User_Balance",owner=self.user3, amount_capital_debt=10)
        self.user4_balance=mommy.make("User_Balance",owner=self.user4, amount_capital_debt=10)
        self.user5_balance=mommy.make("User_Balance",owner=self.user5, amount_capital_debt=10)
        self.user6_balance=mommy.make("User_Balance",owner=self.user6, amount_capital_debt=10)

        self.user2_user_balance=mommy.make("User_User_Balance",owner=self.user2, other_user=self.user1, amount_capital_debt=10)
        self.user3_user_balance=mommy.make("User_User_Balance",owner=self.user3, other_user=self.user1, amount_capital_debt=10)
        self.user4_user_balance=mommy.make("User_User_Balance",owner=self.user4, other_user=self.user1, amount_capital_debt=10)
        self.user5_user_balance=mommy.make("User_User_Balance",owner=self.user5, other_user=self.user1, amount_capital_debt=10)
        self.user6_user_balance=mommy.make("User_User_Balance",owner=self.user6, other_user=self.user1, amount_capital_debt=10)

    def test_add_participant_already_in(self):

        #other_user no need join
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
        self.user2.user_balance.amount=10
        self.user2.user_balance.save()
        self.assertIn('waring:not enough money to',self.activity1.add_participant(self.user2)[1])
        #enougn money
        result=self.activity1.add_participant(self.user3)
        self.assertTrue(result[0],msg=result[1])

    def test_check_out_founder_not_free(self):
        self.user1.user_balance.amount_capital_debt=0
        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        self.activity1.checkout(100)
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
        self.user1.user_balance.amount_capital_debt=0

        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)

        self.activity1.checkout(100)
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
        self.user1.user_balance.amount_capital_debt=0
        self.user2.user_balance.amount_payables_receivables=0
        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        self.activity1.checkout(100)
        user2_user_balance=self.user2.user_user_balance_owner.filter(other_user=self.user1)[0]
        self.assertEqual(user2_user_balance.amount_capital_debt,-7)
        self.assertEqual(user2_user_balance.amount_payables_receivables,0)

        user2_balance=User_Balance.objects.filter(owner=self.user2)[0]
        self.assertEqual(user2_balance.amount_capital_debt,0)
        self.assertEqual(user2_balance.amount_payables_receivables,0)
        fs=Financial_Statement.objects.all()[0]
        print(fs.amount_for_participants/fs.activity.participants.count()+1)
        print(fs.amount_for_participants)
        print(fs.amount_for_founder)
        print(fs.amount_for_founder_profit)
        print(fs.amount_for_system_profit)
        self.assertEqual(0,fs.amount_for_participants
                            -fs.amount_for_founder
                            -fs.amount_for_founder_profit
                            -fs.amount_for_system_profit,
                         'not balance')
        #update balance for each account

    def test_check_out_actual_cost_greater_than_expected(self):
        self.user1.user_balance.amount_capital_debt=0
        self.user2.user_balance.amount_payables_receivables=0
        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        self.activity1.total_cost_actual=200
        self.activity1.checkout(200)
        user2_user_balance=self.user2.user_user_balance_owner.filter(other_user=self.user1)[0]
        self.assertEqual(user2_user_balance.amount_capital_debt,-32)
        self.assertEqual(user2_user_balance.amount_payables_receivables,0)

        user2_balance=User_Balance.objects.filter(owner=self.user2)[0]
        self.assertEqual(user2_balance.amount_capital_debt,0)
        self.assertEqual(user2_balance.amount_payables_receivables,0)


    def test_check_out_actual_cost_less_than_expected(self):
        self.user1.user_balance.amount_capital_debt=0
        self.user2.user_balance.amount_payables_receivables=0
        self.activity1.add_participant(self.user2)
        self.activity1.add_participant(self.user3)
        self.activity1.add_participant(self.user4)
        #self.activity1.total_cost_actual=3
        self.activity1.checkout(3)
        user2_user_balance=self.user2.user_user_balance_owner.filter(other_user=self.user1)[0]
        self.assertEqual(user2_user_balance.amount_capital_debt,10)
        self.assertEqual(user2_user_balance.amount_payables_receivables,0)
        user2_balance=User_Balance.objects.filter(owner=self.user2)[0]
        self.assertEqual(user2_balance.amount_capital_debt,8)
        self.assertEqual(user2_balance.amount_payables_receivables,0)

    def test_check_balance(self):
        """账户余额"""
        self.activity1.total_cost_expected=100
        self.user2_balance.amount_capital_debt=10
        self.activity1.add_participant(self.user2)
        user2_user_balance=self.user2.user_user_balance_owner.filter(other_user=self.user1)[0]
        user2_balance=self.user2.user_balance
        user3_user_balance=self.user2.user_user_balance_owner.filter(other_user=self.user1)[0]
        user3_balance=self.user3.user_balance
        #在线账户 应付款10(标记为-10)
        self.assertEqual(user2_balance.amount_payables_receivables,-10)
        self.assertEqual(user2_balance.amount_capital_debt,0)
        #与 user1 相关的离线账户 资产额为-30
        self.assertEqual(user2_user_balance.amount_capital_debt ,-30)
        self.assertEqual(user2_user_balance.amount_payables_receivables,-40)

        print('amount_capital_debt_before'+str(user3_user_balance.amount_capital_debt))
        self.activity1.add_participant(self.user3)
        user3_user_balance=self.user3.user_user_balance_owner.filter(owner=self.user3,other_user=self.user1)[0]
        print('amount_capital_debt_after'+str(user3_user_balance.amount_capital_debt))

        self.activity1.add_participant(self.user4)
        print('amount_capital_debt4_after'+str(User_User_Balance.objects.filter(owner=self.user4,other_user=self.user1)[0].amount_capital_debt))


        #活动结束,







