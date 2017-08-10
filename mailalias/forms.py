from django import forms
from templates import widgets
from mailmember.models import MailMember

class MailAliasAdd(forms.Form):
    alias = forms.CharField(label='Alias:', widget=widgets.MetroTextInput)
    mailmember = forms.ModelChoiceField(queryset=MailMember.objects.all(), label='user to add:', widget=widgets.MetroSelect)
