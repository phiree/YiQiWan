__author__ = 'Administrator'
from django.conf.urls import patterns, url, include
from .views.front_web_mobile import home, register, register_success, ActivityDetail, join_activity
from .views.my import my_home, create_activity, ActivityCreate, my_settings\
    ,my_joint_activity_list,my_created_activity_list,my_profile,my_balance

urlpatterns = patterns(''

                       , url(r'^accounts/login.*', 'django.contrib.auth.views.login',
                             {'template_name': 'web/m/login.html'}, name='login')
                       , url(r'^account/logout.*', 'django.contrib.auth.views.logout',
                             {'template_name': 'web/m/logout.html'}, name='logout')
                       , url(r'^account/register$', register, name='register')
                       , url(r'^account/register_success$', register_success, name='register_success')
                       , url(r'^$', home, name='site_home')

                       , url(r'^my/$', my_home, name='my_home')
                        , url(r'^my/profile/$',  my_profile ,name='my_profile')
                         , url(r'^my/balance/$',  my_balance ,name='my_balance')
                       , url(r'^my/create_activity$', ActivityCreate.as_view(), name='my_create_activity')
                       , url(r'^my/create_place$', create_activity, name='my_create_place')

                       , url(r'^my/joint_activity/list$', my_joint_activity_list, name='my_joint_activity_list')
                        , url(r'^my/created_activity/list$', my_created_activity_list, name='my_created_activity_list')
                       , url(r'^my/settings/$', my_settings, name='my_settings')

                       ,
                       url(r'^activity_detail/(?P<activity_id>\d+)/$', ActivityDetail.as_view(), name='activity_detail')
                       , url(r'^join_activity/(?P<activity_id>\d+)/$', join_activity, name='join_activity')
                       ,
)
