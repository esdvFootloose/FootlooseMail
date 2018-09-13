from django.conf.urls import url
# from .forms import CaptchaPasswordResetForm
from . import views
# from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

app_name = 'index'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
]