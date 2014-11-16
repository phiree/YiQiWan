from django.shortcuts import render,HttpResponseRedirect
from django.http import HttpResponseRedirect
from ..forms import fm_register,fm_activity
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext  as _,ungettext
from django.views.generic import DetailView
from django.contrib.auth.models import User
from ..models import Activity,User_Balance,User_User_Balance
def home(request):
    activity_list=Activity.objects.all()
    return render(request,'web/m/home.html',{'activity_list':activity_list})

class ActivityDetail(DetailView):
    model = Activity
    template_name = 'web/m/activity_detail.html'
    slug_field = 'id'
    slug_url_kwarg ='activity_id'
def join_activity(request,activity_id):
    result=()
    if request.method=='POST':
        activity=Activity.objects.get(pk=activity_id)
        user=request.user
        result=activity.add_participant(user)
    return render(request,'web/m/join_result.html',{'msg':result})
def join_result(request):
    msg='join ok'

    return render(request,'web/m/join_result.html',{'msg':msg})
def register(request):
    form=  fm_register.RegisterForm()
    if request.method=="POST":
        form=fm_register.RegisterForm(request.POST)
        if form.is_valid():
            created_user=User.objects.create_user(username=form.cleaned_data['username'],
                                     password= form.cleaned_data['password'])
            User_Balance.objects.get_or_create(owner=created_user)
            return HttpResponseRedirect(redirect_to= reverse('web:register_success'))
    return render(request,'web/m/register.html',{'form':form})


def register_success(request):
    return render(request,'web/m/register_success.html',{'msg':_('this is a goodone')})

