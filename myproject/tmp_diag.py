import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from myapp.models import Message

u = User.objects.create_user(username='diag_sender', password='12345')
r = User.objects.create_user(username='diag_recipient', password='12345')
c = Client()
c.force_login(u)
resp = c.post('/messages/diag_recipient/', {'text': 'hello from diagnostic'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
print('status', resp.status_code)
print('content', resp.content.decode())
print('messages', Message.objects.filter(sender=u, recipient=r).count())
