from django.conf.urls import url
from .forms import CaptchaPasswordResetForm
from . import views
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

app_name = 'index'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^$', views.index, name='index'),
    url(r'^reset/$', password_reset, {
        "template_name"             : "GenericForm.html",
        "password_reset_form"       : CaptchaPasswordResetForm,
        "email_template_name"       : "email/password_reset_email.html",
        "html_email_template_name"  : "email/password_reset_email.html",
        "subject_template_name"     : "email/password_reset_mail_subject.txt",
        "post_reset_redirect"       : "index:password_reset_done",
        "from_email"                : "no-reply@esdvfootloose.nl",
    },  name='password_reset'),
    url(r'^reset/send/$', password_reset_done,{
        "template_name" : "base.html",
        "extra_context" : {
            "Message"   : "We've emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly.<br>"
                        "If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder.",
            "return"    : "index:staffLogin",
        }
    }, name='password_reset_done'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, {"template_name" : "password_reset_confirm.html"}, name='password_reset_confirm'),
    url(r'^reset/done/$', password_reset_complete, {
        "template_name" : "base.html",
        "extra_context" : {
            "Message"   : "Your password has been set.  You may go ahead and log in now.",
            "return"    : "index:staffLogin"
        }
    }, name='password_reset_complete'),
    url(r'^about/$', views.about, name='about'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
]