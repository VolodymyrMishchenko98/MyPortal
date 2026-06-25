from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Note, Message


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Ім'я",
        widget=forms.TextInput(attrs={'placeholder': "Ваше ім'я", 'class': 'form-input'}))
    last_name = forms.CharField(max_length=30, required=True, label='Прізвище',
        widget=forms.TextInput(attrs={'placeholder': 'Ваше прізвище', 'class': 'form-input'}))
    email = forms.EmailField(required=True, label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'form-input'}))
    username = forms.CharField(label='Логін',
        widget=forms.TextInput(attrs={'placeholder': 'Оберіть логін', 'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Мінімум 8 символів', 'class': 'form-input'}))
    password2 = forms.CharField(label='Підтвердження пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторіть пароль', 'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Цей email вже використовується.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логін',
        widget=forms.TextInput(attrs={'placeholder': 'Ваш логін', 'class': 'form-input', 'autofocus': True}))
    password = forms.CharField(label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ваш пароль', 'class': 'form-input'}))


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="Ім'я",
        widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=30, required=False, label='Прізвище',
        widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(required=False, label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Profile
        fields = ('bio', 'avatar', 'avatar_color')
        labels = {'bio': 'Про себе', 'avatar': 'Фото профілю', 'avatar_color': 'Колір аватара'}
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Розкажіть про себе...'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input-file'}),
            'avatar_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color'}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'content', 'priority')
        labels = {'title': 'Заголовок', 'content': 'Опис', 'priority': 'Пріоритет'}
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Назва завдання'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Деталі...'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
        }


class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Отримувач',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Message
        fields = ('recipient', 'subject', 'body')
        labels = {'subject': 'Тема', 'body': 'Повідомлення'}
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Тема листа'}),
            'body': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Текст повідомлення...'}),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user:
            self.fields['recipient'].queryset = User.objects.exclude(pk=current_user.pk)
