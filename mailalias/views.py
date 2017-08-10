from django.shortcuts import render
from index.decorators import staff_required
from django.contrib.auth.decorators import login_required
from . import NeoStrada
from django.core.cache import caches
# from mailmember.models import MailMember

@login_required
def listMailAlias(request):
    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]

    if aliasusers.get('keys') is None or useraliasses.get('keys') is None:
        NeoStrada.FetchData()

    aliases = []
    for alias in sorted(aliasusers.get('keys')):
        aliases.append([alias, aliasusers.get(alias, [])])
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

