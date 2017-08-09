from django import template
from django.contrib.auth.models import Group
register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_names):
    if user.is_superuser:
        return True
    for group_name in group_names.split(';'):
        group = Group.objects.get(name=group_name)
        if group in user.groups.all():
            return True

    return False

@register.simple_tag
def GetHash():
    try:
        with open("githash", "r") as stream:
            h = stream.readlines()[0].strip('\n')
        return h[:10]
    except:
        return "None"
