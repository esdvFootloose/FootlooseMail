from django.conf.urls import url
from . import views

app_name = 'tracking'
urlpatterns = [
    url(r'^listchanges/$', views.listChanges, name='listchanges'),
]