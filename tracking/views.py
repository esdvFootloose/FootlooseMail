from django.shortcuts import render
from index.decorators import superuser_required
from .models import AliasChange

@superuser_required
def listChanges(request):
    return render(request, 'tracking/listtracking.html', {
        'changes' : AliasChange.objects.all()
    })