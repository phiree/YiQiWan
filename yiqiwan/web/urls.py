__author__ = 'Administrator'
from django.conf.urls import patterns,url,include
from .views.front import home
from .views.my import  my_home,create_activity,ActivityCreate
urlpatterns=patterns('',
                    url(r'^$', home,name='site_home'),
                    url(r'^my/$', my_home,name='my_home'),
                    url(r'^my/create_activity$',ActivityCreate.as_view(),name='my_create_activity'),
                    url(r'^my/create_place$', create_activity,name='my_create_place')
                     )
