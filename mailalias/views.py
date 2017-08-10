from django.shortcuts import render
from index.decorators import staff_required
from django.contrib.auth.decorators import login_required
from . import NeoStrada
from django.core.cache import caches
from . import forms
# from mailmember.models import MailMember

@login_required
def listMailAlias(request):
    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]

    if aliasusers.get('keys') is None or useraliasses.get('keys') is None:
        NeoStrada.FetchData()

    aliases = []
    for alias in sorted(aliasusers.get('keys')):
        aliases.append([alias.split('@')[0], aliasusers.get(alias, [])])
    #TODO: add mailmember object to provide links in alias list
    return render(request, 'mailalias/mailaliaslist.html', {
        'aliases' : aliases
    })

@staff_required
def fetchData(request):
    NeoStrada.FetchData()
    return render(request, 'base.html', {
        'Message' : 'Aliases cache (re)fetched!'
    })

@staff_required
def clearCache(request):
    caches["aliasusers"].clear()
    caches["useraliasses"].clear()
    caches["default"].clear()

    return render(request, 'base.html', {
        'Message' : 'Cache cleared!'
    })

@staff_required
def addUserToAlias(request):
    if request.method == 'POST':
        form = forms.MailAliasAdd(request.POST)
        if form.is_valid():
            response = NeoStrada.AddToAlias(form.cleaned_data['mailmember'].Email, form.cleaned_data['alias'])
            if response != 200:
                return render(request, 'base.html', {
                    'Message' : 'Something went wrong, responsecode: {}'.format(response)
                })
            else:
                return render(request, 'base.html', {
                    'Message' : 'User {} with email {} added to {}'.format(form.cleaned_data['mailmember'],
                                                                           form.cleaned_data['mailmember'].Email,
                                                                           form.cleaned_data['alias'])
                })
    else:
        form = forms.MailAliasAdd()

    return render(request, 'GenericForm.html', {
        "form" : form,
        "formtitle" : "Add User to Alias",
        "buttontext" : "Add"
    })

@staff_required
def deleteUserFromAlias(request, email, alias):
    aliasusers = caches["aliasusers"]

    if email not in aliasusers.get('{}@esdvfootloose.nl'.format(alias), []):
        return render(request, 'base.html', {
            'Message' : 'User {} is not in alias {}'.format(email, alias)
        })

    response = NeoStrada.RemoveFromAlias(email, alias)
    if response != 200:
        return render(request, 'base.html', {
            'Message': 'Something went wrong, responsecode: {}'.format(response)
        })
    else:
        return render(request, 'base.html', {
            'Message': 'Email {} removed from {}'.format(email, alias)
        })