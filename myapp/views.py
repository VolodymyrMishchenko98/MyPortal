import json
from datetime import timedelta

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db import transaction
from django.db.models import Q, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from .forms import RegisterForm, ProfileForm, NoteForm, MessageForm
from .models import Profile, Note, Message


def _annotate_thread_messages(thread_messages):
    TIME_GAP = timedelta(minutes=15)

    for i, msg in enumerate(thread_messages):
        prev_msg = thread_messages[i - 1] if i > 0 else None
        next_msg = thread_messages[i + 1] if i < len(thread_messages) - 1 else None

        msg.show_time_divider = (
            prev_msg is None or
            msg.created_at - prev_msg.created_at > TIME_GAP
        )
        msg.is_first_in_group = (
            prev_msg is None or
            prev_msg.sender_id != msg.sender_id or
            msg.show_time_divider
        )
        msg.is_last_in_group = (
            next_msg is None or
            next_msg.sender_id != msg.sender_id or
            (next_msg.created_at - msg.created_at > TIME_GAP)
        )

    return thread_messages


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Реєстрація успішна! Ласкаво просимо.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/dashboard/')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Невірний логін або пароль.')
    
    next_param = request.GET.get('next', '/dashboard/')
    return render(request, 'login.html', {'next': next_param})


@login_required
def dashboard(request):
    notes = Note.objects.filter(user=request.user)
    total = notes.count()
    done = notes.filter(done=True).count()
    remaining = total - done
    return render(request, 'dashboard.html', {
        'total': total,
        'done': done,
        'remaining': remaining
    })


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            messages.success(request, 'Профіль оновлено.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'form': form,
        'user': request.user
    })


@login_required
def notes(request):
    filter_type = request.GET.get('filter', 'all')
    notes = Note.objects.filter(user=request.user)

    if filter_type == 'active':
        notes = notes.filter(done=False)
    elif filter_type == 'done':
        notes = notes.filter(done=True)

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Завдання додано.')
            return redirect('notes')
    else:
        form = NoteForm()

    return render(request, 'notes.html', {
        'notes': notes,
        'form': form,
        'filter_type': filter_type
    })


@login_required
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Завдання додано.')
            return redirect('notes')
    return redirect('notes')


@login_required
def toggle_note(request, note_id):
    try:
        note = Note.objects.get(id=note_id, user=request.user)
        note.done = not note.done
        note.save()
    except Note.DoesNotExist:
        pass
    return redirect('notes')


@login_required
def delete_note(request, note_id):
    try:
        note = Note.objects.get(id=note_id, user=request.user)
        note.delete()
        messages.success(request, 'Завдання видалено.')
    except Note.DoesNotExist:
        pass
    return redirect('notes')


@login_required
def messages_list(request):
    dialogs = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values(
        'sender', 'recipient'
    ).annotate(
        last_message_time=Max('created_at')
    ).distinct()

    dialog_users = []
    for dialog in dialogs:
        if dialog['sender'] == request.user.id:
            other_id = dialog['recipient']
        else:
            other_id = dialog['sender']

        try:
            other_user = User.objects.get(id=other_id)
            unread_count = Message.objects.filter(
                sender=other_user, recipient=request.user, is_read=False
            ).count()
            last_msg = Message.objects.filter(
                Q(sender=request.user, recipient=other_user) |
                Q(sender=other_user, recipient=request.user)
            ).last()

            dialog_users.append({
                'user': other_user,
                'unread': unread_count,
                'last_message': last_msg.text if last_msg else '',
                'last_time': last_msg.created_at if last_msg else None
            })
        except User.DoesNotExist:
            pass

    dialog_users.sort(key=lambda x: x['last_time'] or x['user'].date_joined, reverse=True)

    return render(request, 'messages_list.html', {'dialogs': dialog_users})


@login_required
def messages_new(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'messages_new.html', {'users': users})


@login_required
def messages_thread(request, username):
    try:
        recipient = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'Користувач не знайдений.')
        return redirect('messages_list')

    Message.objects.filter(
        sender=recipient, recipient=request.user, is_read=False
    ).update(is_read=True)

    thread_messages = list(Message.objects.filter(
        (Q(sender=request.user, recipient=recipient) |
         Q(sender=recipient, recipient=request.user))
    ).order_by('created_at'))

    _annotate_thread_messages(thread_messages)

    is_last_message_mine = bool(
        thread_messages and thread_messages[-1].sender_id == request.user.id
    )

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            _annotate_thread_messages([message])
            message.is_first_in_group = True
            message.is_last_in_group = True
            message.show_time_divider = False

            if is_ajax:
                html = render_to_string('partials/message_bubble.html', {
                    'message': message,
                    'user': request.user,
                    'is_last_message_mine': True,
                }, request=request)
                return JsonResponse({'success': True, 'message_html': html})

            messages.success(request, 'Повідомлення відправлено.')
            return redirect(f'/messages/{username}/')

        if is_ajax:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        messages.error(request, 'Повідомлення не було відправлено. Перевірте текст повідомлення.')
    else:
        form = MessageForm()

    return render(request, 'messages_thread.html', {
        'thread_messages': thread_messages,
        'form': form,
        'recipient': recipient,
        'user': request.user,
        'is_last_message_mine': is_last_message_mine
    })


@login_required
def delete_account(request):
    if request.method != 'POST':
        return redirect('profile')

    with transaction.atomic():
        profile = Profile.objects.filter(user=request.user).first()
        if profile and profile.avatar:
            profile.avatar.delete(save=False)

        Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user)).delete()
        Note.objects.filter(user=request.user).delete()
        Profile.objects.filter(user=request.user).delete()

        for session in Session.objects.all():
            data = session.get_decoded()
            if data.get('_auth_user_id') == str(request.user.id):
                session.delete()

        request.user.delete()

    logout(request)
    response = redirect('register')
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    return response
