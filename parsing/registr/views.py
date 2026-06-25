from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .forms import RegisterForm, LoginForm, ProfileForm, NoteForm, MessageForm
from .models import Profile, Note, Message


def get_or_create_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'Вітаємо, {user.first_name}! Реєстрація успішна.')
            return redirect('dashboard')
        messages.error(request, 'Будь ласка, виправте помилки у формі.')
    else:
        form = RegisterForm()
    return render(request, 'registr/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'З поверненням, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Невірний логін або пароль.')
    else:
        form = LoginForm()
    return render(request, 'registr/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Ви успішно вийшли з системи.')
    return redirect('login')


@login_required
def dashboard_view(request):
    profile = get_or_create_profile(request.user)
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    notes = request.user.notes.all()
    total_notes = notes.count()
    done_notes = notes.filter(done=True).count()
    pending_notes = notes.filter(done=False).count()
    high_priority = notes.filter(priority='high', done=False).count()
    unread_messages = request.user.received_messages.filter(is_read=False).count()
    recent_notes = notes[:5]
    recent_messages = request.user.received_messages.select_related('sender')[:5]
    context = {
        'profile': profile,
        'total_notes': total_notes,
        'done_notes': done_notes,
        'pending_notes': pending_notes,
        'high_priority': high_priority,
        'unread_messages': unread_messages,
        'recent_notes': recent_notes,
        'recent_messages': recent_messages,
        'completion_pct': int(done_notes / total_notes * 100) if total_notes else 0,
    }
    return render(request, 'registr/dashboard.html', context)


@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        form.fields['email'].initial = request.user.email
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'registr/profile.html', {'form': form, 'profile': profile})


@login_required
def notes_view(request):
    profile = get_or_create_profile(request.user)
    notes = request.user.notes.all()
    filter_by = request.GET.get('filter', 'all')
    if filter_by == 'active':
        notes = notes.filter(done=False)
    elif filter_by == 'done':
        notes = notes.filter(done=True)
    elif filter_by == 'high':
        notes = notes.filter(priority='high', done=False)

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Завдання додано!')
            return redirect('notes')
    else:
        form = NoteForm()
    return render(request, 'registr/notes.html', {
        'notes': notes, 'form': form, 'filter_by': filter_by, 'profile': profile,
        'total': request.user.notes.count(),
        'done_count': request.user.notes.filter(done=True).count(),
    })


@login_required
def note_toggle(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.done = not note.done
    note.save()
    return JsonResponse({'done': note.done})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Завдання видалено.')
    return redirect('notes')


@login_required
def messages_inbox(request):
    profile = get_or_create_profile(request.user)
    inbox = request.user.received_messages.select_related('sender').all()
    sent = request.user.sent_messages.select_related('recipient').all()
    unread_count = inbox.filter(is_read=False).count()
    form = MessageForm(current_user=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST, current_user=request.user)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            messages.success(request, f'Повідомлення надіслано до {msg.recipient.get_full_name() or msg.recipient.username}!')
            return redirect('messages_inbox')
    return render(request, 'registr/messages.html', {
        'inbox': inbox, 'sent': sent, 'form': form,
        'unread_count': unread_count, 'profile': profile,
    })


@login_required
def message_read(request, pk):
    msg = get_object_or_404(Message, pk=pk, recipient=request.user)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    return render(request, 'registr/message_detail.html', {
        'msg': msg, 'profile': get_or_create_profile(request.user)
    })
    