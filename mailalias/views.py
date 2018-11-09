from django.shortcuts import render
from index.decorators import staff_required, superuser_required
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from . import forms
from .models import ProtectedAlias
from django.http import Http404
from django.shortcuts import get_object_or_404
from .utils import fetch_alias, get_api
from django.views.decorators.http import require_http_methods

@login_required
def listMailAlias(request):
    aliasses = fetch_alias(True)
    if aliasses is None:
        return render(request, 'base.html', {
            'message': 'transip api failed'
        })

    for alias in aliasses:
        try:
            obj = ProtectedAlias.objects.get(Alias=alias)
            if obj.Owners.count() == 0:
                obj.delete()
                obj = None
        except ProtectedAlias.DoesNotExist:
            obj = None
        aliasses[alias]['protected'] = obj

    return render(request, 'mailalias/mailaliaslist.html', {
        'aliasses' : aliasses
    })

@staff_required
def fetchData(request):
    fetch_alias(False)
    return render(request, 'base.html', {
        'Message' : 'Aliases cache (re)fetched!',
        'return' : 'mailalias:listall',
    })

@staff_required
def clearCache(request):
    cache.clear()

    return render(request, 'base.html', {
        'Message' : 'Cache cleared!',
        'return': 'mailalias:listall',
    })

@staff_required
def edit_alias(request, alias=None):
    aliasses = fetch_alias(True)
    if alias in aliasses:
        members = aliasses[alias]['members']
    else:
        members = []

    if request.method == 'POST':
        form = forms.MailAliasAdd(alias, members, request.POST)
        if form.is_valid():
            try:
                protected_obj = ProtectedAlias.objects.get(Alias=form.cleaned_data['alias'])
                if protected_obj.Owners.count() == 0:
                    protected_obj.delete()
                if request.user not in protected_obj.Owners.all():
                    return render(request, 'base.html', {
                        'Message': 'Protected alias and you are not owner!',
                        'return': 'mailalias:listall',
                    })
            except ProtectedAlias.DoesNotExist:
                pass

            api = get_api()
            newmembers = list(set(form.cleaned_data['members'] + form.cleaned_data['externals']))
            if form.cleaned_data['new_external'] != "":
                newmembers.append(form.cleaned_data['new_external'])
            response = api.add_to_alias(form.cleaned_data['alias'], newmembers)
            if not response:
                return render(request, 'base.html', {
                    'Message' : 'Something went wrong: {}'.format(api.failure_reason)
                })
            else:
                #TODO: reenable tracking
                # tracking = AliasChange()
                # tracking.User = request.user
                # tracking.Type = 'a'
                # tracking.Alias = form.cleaned_data['alias']
                # tracking.Email = email
                # tracking.save()
                cache.set('api', api, 24*60*60)

                return render(request, 'base.html', {
                    'Message' : 'alias {} saved'.format(form.cleaned_data['alias'])
                })
    else:
        form = forms.MailAliasAdd(alias, members)

    return render(request, 'GenericForm.html', {
        "form" : form,
        "formtitle" : "Add/Edit Alias",
        "buttontext" : "Save"
    })

@staff_required
@require_http_methods(["POST"])
def delete_alias(request, alias):
    api = get_api()
    if not api.delete_alias(alias):
        return render(request, 'base.html', {
            'Message' : 'alias {} could not be deleted: {}'.format(alias, api.failure_reason)
        })
    cache.set('api', api, 24*60*60)

    return render(request, 'base.html', {
        'Message' : 'alias {} deleted'.format(alias)
    })


@superuser_required
def create_protected(request, alias):
    aliasses = fetch_alias(True)

    if alias not in aliasses:
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
def edit_protected(request, pk):
    obj = get_object_or_404(ProtectedAlias, pk=pk)

    aliasses = fetch_alias(True)


    if obj.Alias not in aliasses:
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