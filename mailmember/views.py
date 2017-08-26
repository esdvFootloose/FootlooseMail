from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from index.decorators import staff_required
from .models import MailMember

@staff_required
def listMailMembers(request):
    return render(request, 'mailmember/mailmemberlist.html', {
        'members' : MailMember.objects.all(),
    })