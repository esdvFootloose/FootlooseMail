from django import forms
from templates import widgets
from .models import ProtectedAlias
from .wordpress import WordPress


class MailAliasAdd(forms.Form):
    alias = forms.CharField(label='Alias:', widget=widgets.MetroTextInput)
    members = forms.MultipleChoiceField(choices=(), label='members:', widget=widgets.MetroSelectMultiple, required=False)
    externals = forms.MultipleChoiceField(choices=(), label='externals:', widget=widgets.MetroSelectMultiple, required=False)
    new_external = forms.CharField(label='New external:', widget=widgets.MetroTextInput, required=False)

    def __init__(self, alias, members, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _, allmembers = WordPress.get_students_data()
        choices = []
        for member in allmembers:
            choices.append((member[-1], '{} {}'.format(member[1], member[2])))
        all_member_emails = [x[-1] for x in allmembers]
        initial_members = []
        initial_externals = []
        if members is not None:
            for member in members:
                if member in all_member_emails:
                    initial_members.append(member)
                else:
                    initial_externals.append(member)
        self.fields['members'].choices = choices
        self.fields['externals'].choices = [(x, x) for x in initial_externals]
        self.initial['alias'] = alias
        self.initial['members'] = initial_members
        self.initial['externals'] = initial_externals

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data['externals'] and not cleaned_data['members'] and not cleaned_data['new_external']:
            raise forms.ValidationError('Alias cannot be empty')
        self.cleaned_data['alias'] = self.cleaned_data['alias'].split("@")[0]
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