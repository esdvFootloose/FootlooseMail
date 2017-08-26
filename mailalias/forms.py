from django import forms
from templates import widgets
from mailmember.models import MailMember
from .models import ProtectedAlias


class MailAliasAdd(forms.Form):
    alias = forms.CharField(label='Alias:', widget=widgets.MetroTextInput)
    mailmember = forms.ModelChoiceField(queryset=MailMember.objects.all(), label='user to add:', widget=widgets.MetroSelect)


class ProtectedAliasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Alias'].disabled = True

    class Meta:
        model = ProtectedAlias
        fields = ['Alias', 'Owners']
        widgets = {
            'Alias' : widgets.MetroTextInput,
            'Owners' : widgets.MetroSelectMultiple,
        }