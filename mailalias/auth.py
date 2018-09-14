from django.contrib.auth.models import User
from subprocess import check_output
import json
import logging

logger = logging.getLogger('django')

class WordpressAuthBackend:
    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        wp_user = check_output(['php', '/usr/share/nginx/html/api-ext-auth.php', username, password])
        try:
            wp_user = json.loads(wp_user.decode())
        except:
            return None
        if 'administrator' not in wp_user['roles'] and 'bestuur' not in wp_user['roles']:
            return None
        try:
            django_user = User.objects.get(username=wp_user['username'])
        except User.DoesNotExist:
            try:
               django_user = User.objects.get(email=wp_user['email'])
            except User.DoesNotExist:
                django_user = User(username=wp_user['username'], email=wp_user['email'])
        django_user.username = wp_user['username']
        django_user.email = wp_user['email']
        django_user.is_staff = True
        django_user.save()
        return django_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
