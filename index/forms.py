from django import forms
from templates import widgets
from django.contrib.auth.forms import PasswordResetForm
from captcha.fields import ReCaptchaField
from django.contrib.auth.models import User
from django.conf import settings
import re

mailPattern = re.compile(settings.EMAILREGEXCHECK)

class CaptchaPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Email", max_length=254, widget=widgets.MetroTextInput)
    captcha = ReCaptchaField()

    def clean_email(self):
        data = self.cleaned_data['email']
        if data == '' or data is None:
            return data
        email = data.strip('\n').strip()
        if not mailPattern.match(email.strip('\r')):
            raise forms.ValidationError("Invalid email address: This should be one TU/e email address")
        domain = email.strip('\r').split('@')[1]
        domain_list = ["tue.nl"]
        if domain not in domain_list:
            raise forms.ValidationError("Please only enter *@tue.nl email addresses")
        return data

    def get_users(self, email):
        users = User.objects.filter(email__iexact=email)
        return users

class LoginForm(forms.Form):
    username = forms.CharField(label='Your username:', max_length=100, min_length=2)
    password = forms.CharField(label='Your password:', max_length=100, min_length=4)

class RegistrationForm(forms.Form):
    username = forms.CharField(label='UserName:', max_length=100, min_length=2, widget=widgets.MetroTextInput)
    firstname = forms.CharField(label='First Name:', max_length=100, min_length=1, widget=widgets.MetroTextInput)
    lastname = forms.CharField(label='Last Name:', max_length=100, min_length=1, widget=widgets.MetroTextInput)
    email = forms.EmailField(label='Email Address:', widget=widgets.MetroEmailInput)
    backendlogin = forms.BooleanField(label='Backend Login Enabled:', widget=widgets.MetroCheckBox, required=False,
                                      initial=False)
    group = forms.ChoiceField(label='Type Staff:', widget=widgets.MetroSelect)

    def __init__(self, groups=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].choices = groups