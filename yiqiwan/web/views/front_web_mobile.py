from django.contrib.auth.decorators import login_required
from django.shortcuts import render,HttpResponseRedirect
from django.http import HttpResponseRedirect
from ..forms import fm_register,fm_activity
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext  as _,ungettext
from django.views.generic import DetailView
from django.contrib.auth import login
from ..models import Activity,User_Balance,User_User_Balance,User2
def home(request):
    activity_list=Activity.objects.all()
    return render(request,'web/m/home.html',{'activity_list':activity_list})

class ActivityDetail(DetailView):
    model = Activity
    template_name = 'web/m/activity_detail.html'
    slug_field = 'id'
    slug_url_kwarg ='activity_id'
    def get_object(self):
        activity=super(ActivityDetail,self).get_object()
        if self.request.user.pk:
            test_result=activity.is_allow_joint(self.request.user)
        else:
            test_result=activity.is_allow_joint_to_all()
        return (activity,test_result)
@login_required
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
            created_user=User2.objects.create_user(username=form.cleaned_data['username'],
                                     password= form.cleaned_data['password'])
            User_Balance.objects.get_or_create(owner=created_user)
            created_user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user=created_user)
            return HttpResponseRedirect(redirect_to= reverse('web:my_interest'))
    return render(request,'web/m/register.html',{'form':form})


def register_success(request):
    return HttpResponseRedirect(reverse('web:my_interest'))
    #return render(request,'web/m/my/interest.html',{'msg':_('this is a goodone')})

