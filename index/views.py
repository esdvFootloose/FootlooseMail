from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template import loader
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.urls.base import  reverse
from index.decorators import superuser_required
from django.utils.html import strip_tags
from django.core.cache import cache

def gotoNextOrHome(request):
    if 'next' in request.GET.keys():
        print(request.GET["next"])
        return HttpResponseRedirect(str(request.GET["next"]))
    return HttpResponseRedirect('/')

def index(request):
    return render(request, "index.html")


def logout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    auth_logout(request)
    return render(request, "base.html", {"Message":"You are now logged out. <a href='/' title='Home'>Go back to the homepage</a>"})


def send_mail(subject_template_name, email_template_name,
              context, from_email, to_email, html_email_template_name=None):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    if ".txt" in subject_template_name:
        subject = loader.render_to_string(subject_template_name, context)
    else:
        subject = subject_template_name
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, strip_tags(body), from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    try:
        email_message.send()
    except:
        with open("mailcrash.log", "a") as stream:
            if html_email_template_name is not None:
                stream.write("Mail to {} could not be send:\n{}\n".format(to_email, html_email))
            else:
                stream.write("Mail to {} could not be send:\n{}\n".format(to_email, body))


@superuser_required
def clearCache(request):
    cache.clear()
    return render(request, "base.html", {"Message":"Cache cleared!"})

@superuser_required
def registerUser(request):
    grps = []
    for grp in Group.objects.all():
        grps.append((grp.id, grp.name))

    if request.method == "POST":
        form = RegistrationForm(grps, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            if User.objects.filter(username=username).exists():
                return render(request, "base.html", {
                    "Message"   : "User with username {} already exists!".format(username),
                    "return"    : "index:registerUser",
                })
            email = form.cleaned_data['email'].lower()
            if User.objects.filter(email=email).exists():
                return render(request, "base.html", {
                    "Message"   : "User with email {} already exists!".format(email),
                    "return"    : "index:registerUser",
                })
            NewUser = User.objects.create_user(username, email, None)
            NewUser.first_name = form.cleaned_data['firstname']
            NewUser.last_name = form.cleaned_data['lastname']
            NewUser.is_staff = form.cleaned_data['backendlogin']
            NewUser.groups.add(Group.objects.get(pk=form.cleaned_data['group']))
            NewUser.save()
            current_site = get_current_site(request)
            domain = current_site.domain
            context = {
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(NewUser.pk)),
                'user': NewUser,
                'token': default_token_generator.make_token(NewUser),
            }
            send_mail("email/password_set_email_subject.txt", "email/password_newuser_set_email.html", context,
                      "no-reply@esdvfootloose.nl", NewUser.email, html_email_template_name="email/password_newuser_set_email.html")

            return render(request, "base.html", {
                "Message"   : "User created and notified",
                "return"    : "index:registerUser",
            })
    else:
        form = RegistrationForm(groups=grps)

    return render(request,"GenericForm.html",{
        "form"      : form,
        "formtitle" : "Register New User",
        "buttontext": "Register",
    })

@login_required
def profile(request):

    vars = {

    }

    return render(request, "profile.html",vars)


def login(request):
    if request.user.is_authenticated:
        return gotoNextOrHome(request)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            #username = form.cleaned_data['username'].lower()
            #if User.objects.filter(username=username).exists():
            #    userobj = User.objects.get(username=username)
            #elif User.objects.filter(email=username).exists():
            #    userobj = User.objects.get(email=username)
            #else:
            #    return render(request, "base.html", {
            #        "Message": "This accountname does not exist, you can <a href=\"{}\">try again with your email</a>."
            #                   "Otherwise contact the dev team at info@FootlooseMail.nl".format(reverse('index:login'))})

            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request,user)
                    return gotoNextOrHome(request)
                else:
                    return render(request, "base.html", {"Message" : "Login failed, your account is deactivated. Please contact the support staff."})
            else:
                return render(request, "base.html", {
                    "Message": "Login failed, incorrect password. Please <a href='" + reverse(
                        "index:login") + "'>try again</a>"})
    form = LoginForm()
    get = ''
    if 'next' in request.GET.keys():
        if request.GET['next']:
           get = "?next="+request.GET['next']
    return render(request, "login.html", {'form': form, 'get': get})


def about(request):
    return render(request, "about.html")
