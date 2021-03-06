from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yiqiwan.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'',include('web.urls',namespace ='web')),
    url(r'^region/',include('region.urls',namespace ='region')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls'))
    , (r'^i18n/', include('django.conf.urls.i18n'))
)
