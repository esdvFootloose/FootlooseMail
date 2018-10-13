from django import forms
from templates import widgets
from .models import ProtectedAlias
from .wordpress import WordPress


class MailAliasAdd(forms.Form):
    alias = forms.CharField(label='Alias:', widget=widgets.MetroTextInput)
    member = forms.ChoiceField(choices=(), label='user to add:', widget=widgets.MetroSelect, required=False)
    email = forms.EmailField(label='Email to add', widget=widgets.MetroTextInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _, members = WordPress.get_students_data()
        choices = [(None, None)]
        for member in members:
            choices.append((member[-1], '{} {}'.format(member[1], member[2])))
        self.fields['member'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get('member')
        email = cleaned_data.get('email')

        if member and email:
            #both are filled in
            raise forms.ValidationError('Please fill in only one of the two fields for email to add')
        if (member is None or member == "") and (email is None or email == ""):
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