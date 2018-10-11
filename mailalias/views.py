from django.shortcuts import render
from index.decorators import staff_required, superuser_required
from django.contrib.auth.decorators import login_required
from . import NeoStrada
from django.core.cache import caches
from . import forms
from .models import ProtectedAlias
from django.http import Http404
from django.shortcuts import get_object_or_404
from tracking.models import AliasChange

@login_required
def listMailAlias(request):
    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]

    if aliasusers.get('keys') is None or useraliasses.get('keys') is None:
        NeoStrada.FetchData()

    aliases = []
    for alias in sorted(aliasusers.get('keys')):
        try:
            obj = ProtectedAlias.objects.get(Alias=alias)
            if obj.Owners.count() == 0:
                obj.delete()
                obj = None
        except ProtectedAlias.DoesNotExist:
            obj = None
        aliases.append([alias.split('@')[0], aliasusers.get(alias, []), obj])
    #TODO: add mailmember object to provide links in alias list
    return render(request, 'mailalias/mailaliaslist.html', {
        'aliases' : aliases
    })

@staff_required
def fetchData(request):
    NeoStrada.FetchData()
    return render(request, 'base.html', {
        'Message' : 'Aliases cache (re)fetched!',
        'return' : 'mailalias:listall',
    })

@staff_required
def clearCache(request):
    caches["aliasusers"].clear()
    caches["useraliasses"].clear()
    caches["default"].clear()

    return render(request, 'base.html', {
        'Message' : 'Cache cleared!',
        'return': 'mailalias:listall',
    })

@staff_required
def addUserToAlias(request):
    if request.method == 'POST':
        form = forms.MailAliasAdd(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('member') is not None:
                email = form.cleaned_data.get('member')
            elif form.cleaned_data.get('email') is not None:
                email = form.cleaned_data.get('email')
            try:
                protected_obj = ProtectedAlias.objects.get(Alias='{}@esdvfootloose.nl'.format(form.cleaned_data['alias']))
                if protected_obj.Owners.count() == 0:
                    protected_obj.delete()
                if request.user not in protected_obj.Owners.all():
                    return render(request, 'base.html', {
                        'Message': 'Protected alias and you are not owner!',
                        'return': 'mailalias:listall',
                    })
            except ProtectedAlias.DoesNotExist:
                pass

            response = NeoStrada.AddToAlias(email, form.cleaned_data['alias'])
            if response != 200:
                return render(request, 'base.html', {
                    'Message' : 'Something went wrong, responsecode: {}'.format(response)
                })
            else:
                tracking = AliasChange()
                tracking.User = request.user
                tracking.Type = 'a'
                tracking.Alias = form.cleaned_data['alias']
                tracking.Email = email
                tracking.save()

                return render(request, 'base.html', {
                    'Message' : 'email {} added to alias {}'.format(email,
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

    try:
        protected_obj = ProtectedAlias.objects.get(Alias='{}@esdvfootloose.nl'.format(alias))
        if protected_obj.Owners.count() == 0:
            protected_obj.delete()
        if request.user not in protected_obj.Owners.all():
            return render(request, 'base.html', {
                'Message' : 'Protected alias and you are not owner!',
                'return' : 'mailalias:listall',
            })
    except ProtectedAlias.DoesNotExist:
        pass

    response = NeoStrada.RemoveFromAlias(email, alias)
    if response != 200:
        return render(request, 'base.html', {
            'Message': 'Something went wrong, responsecode: {}'.format(response)
        })
    else:
        tracking = AliasChange()
        tracking.User = request.user
        tracking.Type = 'd'
        tracking.Alias = alias
        tracking.Email = email
        tracking.save()
        return render(request, 'base.html', {
            'Message': 'Email {} removed from {}'.format(email, alias)
        })

@superuser_required
def createProtected(request, alias):
    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]

    if '@' not in alias:
        alias = '{}@esdvfootloose.nl'.format(alias)

    if aliasusers.get('keys') is None or useraliasses.get('keys') is None:
        NeoStrada.FetchData()

    if alias not in aliasusers.get('keys'):
        raise Http404()

    try:
        obj = ProtectedAlias.objects.get(Alias=alias)
    except ProtectedAlias.DoesNotExist:
        obj = ProtectedAlias(Alias=alias)
        obj.save()

    if request.method == 'POST':
        form = forms.ProtectedAliasForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {
                'Message' : 'Protected alias saved!',
                'return' : 'mailalias:listall'
            })
    else:
        form = forms.ProtectedAliasForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Protect Alias',
        'buttontext' : 'Protect'
    })

@superuser_required
def editProtected(request, pk):
    obj = get_object_or_404(ProtectedAlias, pk=pk)

    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]

    if aliasusers.get('keys') is None or useraliasses.get('keys') is None:
        NeoStrada.FetchData()

    if obj.Alias not in aliasusers.get('keys'):
        obj.delete()
        return render(request, 'base.html' , {
            'Message' : 'Alias no longer exists, object deleted',
            'return' : 'mailalias:listall'
        })

    if request.method == "POST":
        form = forms.ProtectedAliasForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            return render(request, 'base.html', {
                'Message' : 'Protected alias {} saved!'.format(obj),
                'return' : 'mailalias:listall'
            })
    else:
        form = forms.ProtectedAliasForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Protect Alias',
        'buttontext' : 'Protect'
    })