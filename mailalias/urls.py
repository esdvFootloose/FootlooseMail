from django.conf.urls import url
from . import views

app_name = 'mailalias'
urlpatterns = [
    url(r'^list/$', views.listMailAlias, name='listall'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
    url(r'^refetch/$', views.fetchData, name='refetch'),
    url(r'^adduser/$', views.addUserToAlias, name='adduser'),
    url(r'^deleteuser/(?P<alias>[\w\-]+)/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$$',
        views.deleteUserFromAlias, name='deleteuser'),
]