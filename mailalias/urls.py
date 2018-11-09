from django.conf.urls import url
from . import views

app_name = 'mailalias'
urlpatterns = [
    url(r'^list/$', views.listMailAlias, name='listall'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
    url(r'^refetch/$', views.fetchData, name='refetch'),
    url(r'^adduser/(?P<alias>[\w\-]+)/$', views.edit_alias, name='adduser'),
    url(r'^adduser/$', views.edit_alias, name='adduser'),
    url(r'^delete/(?P<alias>[\w\-]+)/$', views.delete_alias, name='deletealias'),
    url(r'^protected/(?P<pk>[0-9]+)/$', views.edit_protected, name='editprotected'),
    url(r'^protected/(?P<alias>[\w\-]+)/$', views.create_protected, name='createprotected'),
]