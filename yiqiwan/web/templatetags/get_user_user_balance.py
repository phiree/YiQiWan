from django.template import Library
from ..models import  User_User_Balance,User2
register = Library()

@register.filter
def get_balance(value,arg):
    """
return the balance_account.
    """
    other_user=User2.objects.get(pk=arg)
    balance,created=User_User_Balance.objects.get_or_create(owner=other_user,other_user= value)
    return (balance.amount_capital_debt,balance.amount_receivables_payables)

