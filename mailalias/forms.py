from django import forms
from templates import widgets
from mailmember.models import MailMember
from .models import ProtectedAlias


class MailAliasAdd(forms.Form):
    alias = forms.CharField(label='Alias:', widget=widgets.MetroTextInput)
    mailmember = forms.ModelChoiceField(queryset=MailMember.objects.all(), label='user to add:', widget=widgets.MetroSelect, required=False)
    email = forms.EmailField(label='Email to add', widget=widgets.MetroTextInput, required=False)

    def clean(self):
        cleaned_data = super().clean()
        mailmember = cleaned_data.get('mailmember')
        email = cleaned_data.get('email')

        if mailmember and email:
            #both are filled in
            raise forms.ValidationError('Please fill in only one of the two fields for email to add')
        if mailmember is None and (email is None or email == ""):
            #none are filled in
            raise forms.ValidationError('Please fill in one of the fields to add email')

        return cleaned_data

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