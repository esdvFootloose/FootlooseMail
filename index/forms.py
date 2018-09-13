from django import forms
from templates import widgets
from django.conf import settings
import re

mailPattern = re.compile(settings.EMAILREGEXCHECK)

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