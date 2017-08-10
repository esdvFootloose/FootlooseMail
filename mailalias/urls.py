from django.conf.urls import url
from . import views

app_name = 'mailalias'
urlpatterns = [
    url(r'^list/$', views.listMailAlias, name='listall'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
    url(r'^refetch/$', views.fetchData, name='refetch'),
]