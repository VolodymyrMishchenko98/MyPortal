from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
from myapp.models import Message

User.objects.all().delete()
Message.objects.all().delete()
sender = User.objects.create_user(username='s', password='p')
recipient = User.objects.create_user(username='r', password='p')
first = Message.objects.create(sender=sender, recipient=recipient, text='first', is_read=True)
second = Message.objects.create(sender=sender, recipient=recipient, text='second', is_read=True)
third = Message.objects.create(sender=sender, recipient=recipient, text='third', is_read=True)

first.created_at = timezone.now() - timedelta(minutes=20)
first.save(update_fields=['created_at'])
second.created_at = timezone.now() - timedelta(minutes=5)
second.save(update_fields=['created_at'])
third.created_at = timezone.now()
third.save(update_fields=['created_at'])

thread_messages = list(Message.objects.filter(
    (Q(sender=sender, recipient=recipient) | Q(sender=recipient, recipient=sender))
).order_by('created_at'))

TIME_GAP = timedelta(minutes=15)
for i, msg in enumerate(thread_messages):
    prev_msg = thread_messages[i - 1] if i > 0 else None
    msg.show_time_divider = (prev_msg is None or msg.created_at - prev_msg.created_at > TIME_GAP)
    print(i, msg.text, 'prev=', prev_msg.text if prev_msg else None, 'gap=', (msg.created_at - prev_msg.created_at).total_seconds() if prev_msg else None, 'divider=', msg.show_time_divider)
