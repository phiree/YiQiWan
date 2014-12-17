__author__ = 'phiree'
from django.conf.urls import patterns, url
from .views import *
urlpatterns = patterns(''
    ,url(r'^region_list/(?P<parent_id>\d+)/$', get_region_list,name='region_list')
    ,url(r'^region_tab/$', region_tab,name='region_tab')
)