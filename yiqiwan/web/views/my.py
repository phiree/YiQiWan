from django.shortcuts import render,HttpResponseRedirect
from django.forms import  ModelForm
from django.views.generic import CreateView
from ..forms import fm_activity
from ..models import Activity
from django.core.urlresolvers import reverse
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
            'founder':self.request.user
        }
    def form_valid(self, form):
        user = self.request.user
        form.instance.founder = user
        return super(ActivityCreate, self).form_valid(form)




