# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,HttpResponseRedirect
from django.forms import  ModelForm
from django.views.generic import CreateView
from ..forms import fm_activity
from ..forms.fm_my import fm_charge_activity,fm_interest
from ..models import Activity,User_User_Balance,User_Balance\
    ,Base_Balance,User2,Balance_Flow,flow_type_choice,Place,Interest,User_Scope
from region.models import Region
from django.core.urlresolvers import reverse
from ..biz import balance as biz_balance
from django.utils import timezone as DateTime

from django.utils.translation import gettext as _
from django.http import JsonResponse
@login_required
def my_home(request):
        return render(request,'web/m/my/home.html')
#todo
""""
创建活动要用向导的形式 1)活动地点-->2)名称,活动类型->3)开始时间,结束时间,报名截止时间->4)参加人数,最多参加人数
->5)参加人数,最多参加人数
"""
def create_place(request):

    if request.method=='GET':
        fm=fm_activity.ActivityForm()
        pass
    elif request.method=="POST":
        instance=request.POST
        instance.founder=request.user
        fm=fm_activity.ActivityForm(instance)

        except_msg=''
        if fm.is_valid():
            try:
                fm_model=fm.save(commit=False)
                m=Activity()
                fm_model.status=m.status

                return HttpResponseRedirect('web/m/my/create_succes.html')
            except AttributeError as e:
                except_msg=e
                pass
    return render(request,'web/m/my/create_activity.html',{'form':fm,'except_msg':except_msg})
class ActivityCreate(CreateView):
    model=Activity
    form_class =fm_activity.ActivityForm
    template_name = 'web/m/my/create_activity.html'

    def get_success_url(self):
        return reverse('web:my_home')
    def get_initial(self):

        return{
            'other_user':self.request.user
        }
    def form_valid(self, form):
        address=self.request.POST.get('address')
        place,created=Place.objects.get_or_create(name=address,address=address,
                                                 coordinate_x=1,coordinate_y=1,
                                                 owner=self.request.user,
                                                 phone='',
                                                 )

        form.instance.status='Open'
        user = self.request.user
        form.instance.founder = user
        form.instance.place=place
        return super(ActivityCreate, self).form_valid(form)

def my_settings(request):

    return render(request,'web/m/my/settings.html',{'redirect_to':reverse('web:my_home')})
    pass

def my_joint_activity_list(request):

    activity_list=request.user.activity_participants.all()
    return render(request,'web/m/my/joint_activity_list.html',{'activity_list':activity_list})

def my_created_activity_list(request):
    activity_list=Activity.objects.filter(founder=request.user)
    return render(request,'web/m/my/created_activity_list.html',{'activity_list':activity_list})
def my_profile(request):

    return render(request,'web/m/my/profile.html')

def my_balance(request):

    balance_online=request.user.user_balance
    balance_offline_summary=request.user.get_user_offline_balance_summary()

    return render(request,'web/m/my/balance.html',{'balance_online':balance_online,
                                                   'balance_offline_summary':balance_offline_summary,
                                                     })

#活动收款界面
def my_charge_activity(request,activity_id):

    activity=Activity.objects.get(pk=activity_id)
    if request.method=='POST':
        form=fm_charge_activity(request.POST)
        if form.is_valid():
            charge_user=User2.objects.get(pk=form.cleaned_data['charge_user_id'])
            amount=form.cleaned_data['amount']
            account=charge_user.get_user_user_balance(request.user)[0]

            flow=Balance_Flow.objects.create(flow_type=flow_type_choice[3][0],
                                        account=account,
                                        amount=amount,
                                        occur_time=DateTime.now(),
                                        activity=activity,
                                        )
            flow.apply_flow()
            account=charge_user.get_user_user_balance(request.user)[0]
            return JsonResponse({'result:':True,'balance':{'capital':account.amount_capital_debt,'payables':account.amount_receivables_payables }})
        else:
            return JsonResponse({'result':False,'errmsg':form.errors})

    return render(request,'web/m/my/charge_activity.html',{'activity':activity})


def charge(request,from_user, to_user,activity=None):
    pass


def my_balance_flow_list(request):
    return my_balance_flow_list(request,None)


def my_balance_flow_list_for_account(request,account_id):
    flow_list=biz_balance.get_user_balance_flow(request.user,account_id)
    return render(request,'web/m/my/balance_flow_list.html',{'flow_list':flow_list})


def my_interest(request):
    form=fm_interest(instance=request.user)
    msg=''
    if request.method=='POST':
        form=fm_interest( request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            msg='保存成功'

    return render(request,'web/m/my/interest.html',{'form':form,'msg':msg})

def my_scope(request):
    scopes=User_Scope.objects.all().order_by('-last_updated')
    return render(request,'web/m/my/scope.html',{'scopes':scopes})

def update_scope(request):
    if request.method=='POST':
        region_id=request.POST.get('region_id')
        region=Region.objects.get(region_id=region_id)
        User_Scope.objects.create(user=request.user,region=region,last_updated=DateTime.now())
        return JsonResponse({'result':'ok'})

def delete_scope(request):
    if request.method=='POST':
        user_scope_id=request.POST.get('user_scope_id')
        User_Scope.objects.get(pk=user_scope_id).delete()
        return JsonResponse({'result':'ok'})
