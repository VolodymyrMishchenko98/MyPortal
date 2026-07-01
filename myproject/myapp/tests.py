from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Message


class MessagesThreadGroupingTests(TestCase):
    def test_thread_context_includes_grouping_flags(self):
        sender = User.objects.create_user(username='sender', password='testpass123')
        recipient = User.objects.create_user(username='recipient', password='testpass123')
        self.client.force_login(sender)

        first = Message.objects.create(sender=sender, recipient=recipient, text='first', is_read=True)
        second = Message.objects.create(sender=sender, recipient=recipient, text='second', is_read=True)
        third = Message.objects.create(sender=sender, recipient=recipient, text='third', is_read=True)

        first.created_at = timezone.now() - timedelta(minutes=20)
        first.save(update_fields=['created_at'])

        second.created_at = timezone.now() - timedelta(minutes=10)
        second.save(update_fields=['created_at'])

        third.created_at = timezone.now()
        third.save(update_fields=['created_at'])

        response = self.client.get(reverse('messages_thread', args=[recipient.username]))

        self.assertEqual(response.status_code, 200)
        messages = list(response.context['thread_messages'])
        self.assertEqual(len(messages), 3)

        self.assertTrue(messages[0].show_time_divider)
        self.assertFalse(messages[1].show_time_divider)
        self.assertFalse(messages[2].show_time_divider)
        self.assertTrue(messages[0].is_first_in_group)
        self.assertFalse(messages[0].is_last_in_group)
        self.assertFalse(messages[1].is_first_in_group)
        self.assertFalse(messages[1].is_last_in_group)
        self.assertTrue(messages[2].is_last_in_group)
        self.assertTrue(response.context['is_last_message_mine'])

    def test_ajax_invalid_message_post_returns_json_error(self):
        sender = User.objects.create_user(username='ajax_sender', password='testpass123')
        recipient = User.objects.create_user(username='ajax_recipient', password='testpass123')
        self.client.force_login(sender)

        response = self.client.post(
            reverse('messages_thread', args=[recipient.username]),
            {'text': ''},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')
        payload = response.json()
        self.assertFalse(payload['success'])
        self.assertIn('text', payload['errors'])
        self.assertEqual(Message.objects.count(), 0)
