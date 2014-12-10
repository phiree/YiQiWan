__author__ = 'Administrator'
from django.conf.urls import patterns, url, include
from .views.front_web_mobile import home, register, register_success, ActivityDetail, join_activity

from .views import my
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = patterns(''

                       , url(r'^accounts/login.*', 'django.contrib.auth.views.login',
                             {'template_name': 'web/m/login.html'}, name='login')
                       , url(r'^account/logout.*', 'django.contrib.auth.views.logout',
                             {'template_name': 'web/m/logout.html'}, name='logout')
                       , url(r'^account/register$', register, name='register')
                       , url(r'^account/register_success$', register_success, name='register_success')
                       , url(r'^$', home, name='site_home')

                       , url(r'^my/$', my.my_home, name='my_home')
                        , url(r'^my/profile/$',  my.my_profile ,name='my_profile')
                         , url(r'^my/balance/$',  my.my_balance ,name='my_balance')
                         , url(r'^my/balance/flow_list/$',  my.my_balance_flow_list ,name='my_balance_flow_list')
                          , url(r'^my/balance/flow_list_for_account/(?P<account_id>\d+)$',  my.my_balance_flow_list_for_account ,name='my_balance_flow_list_for_account')
                       , url(r'^my/create_activity$', my.ActivityCreate.as_view(), name='my_create_activity')
                       , url(r'^my/create_place$', my.create_place, name='my_create_place')
                       , url(r'^my/my_interest$', my.my_interest, name='my_interest')

                       , url(r'^my/joint_activity/list$', my.my_joint_activity_list, name='my_joint_activity_list')
                        , url(r'^my/created_activity/list$', my.my_created_activity_list, name='my_created_activity_list')
                        , url(r'^my/charge_activity/(?P<activity_id>\d+)/$', my.my_charge_activity, name='my_charge_activity')
                       , url(r'^my/settings/$', my.my_settings, name='my_settings')

                       ,
                         url(r'^activity_detail/(?P<activity_id>\d+)/$', ActivityDetail.as_view(), name='activity_detail')
                       , url(r'^join_activity/(?P<activity_id>\d+)/$', join_activity, name='join_activity')
                       ,
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
