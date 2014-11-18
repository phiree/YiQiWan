from django.contrib.auth.decorators import login_required
from django.shortcuts import render,HttpResponseRedirect
from django.forms import  ModelForm
from django.views.generic import CreateView
from ..forms import fm_activity
from ..models import Activity,User_User_Balance,User_Balance,Base_Balance
from django.core.urlresolvers import reverse

@login_required
def my_home(request):
        return render(request,'web/m/my/home.html')

def create_activity(request):

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
        form.instance.status='Open'
        user = self.request.user
        form.instance.founder = user
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
    balance_offline_list_owner=request.user.user_user_balance_owner.all()
    balance_offline_list_other_user=request.user.user_user_balance_other_user.all()

    return render(request,'web/m/my/balance.html',{'balance_online':balance_online,
                                                   'balance_offline_list_owner':balance_offline_list_owner,
                                                   'balance_offline_list_other_user':balance_offline_list_other_user
                                                    })


