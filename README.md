# МійChat

Персональний веб-портал з управлінням завданнями, внутрішніми повідомленнями та профілем користувача. Побудований на Django з чистим мінімалістичним інтерфейсом.

---

## Можливості

- **Дашборд** — статистика завдань, прогрес виконання, останні завдання та повідомлення
- **Завдання** — створення, фільтрація (всі / активні / виконані / термінові), пріоритети, позначення виконаних
- **Повідомлення** — внутрішня пошта між користувачами, вхідні та надіслані
- **Профіль** — редагування імені, прізвища, email, bio, аватару та кольору аватара
- **Авторизація** — реєстрація, вхід, вихід

---

## Стек

| Компонент | Версія |
|-----------|--------|
| Python | 3.12 |
| Django | 6.0.6 |
| Pillow | 12.2.0 |
| SQLite | вбудована |
| HTML/CSS | власні стилі, без фреймворків |

---

## Структура проекту

```
parsing/
├── manage.py
├── parsing/              # Конфігурація Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── registr/              # Основний додаток
│   ├── models.py         # Profile, Note, Message
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   ├── templates/
│   │   └── registr/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── notes.html
│   │       ├── messages.html
│   │       ├── message_detail.html
│   │       ├── profile.html
│   │       ├── login.html
│   │       └── register.html
│   └── static/
│       └── registr/
│           └── css/
│               ├── base.css
│               ├── auth.css
│               ├── dashboard.css
│               ├── notes.css
│               ├── messages.css
│               └── profile.css
├── media/                # Аватари користувачів
└── staticfiles/          # Зібрана статика (collectstatic)
```

---

## Моделі

### `Profile`
Розширення стандартного `User` через `OneToOneField`.

| Поле | Тип | Опис |
|------|-----|------|
| `user` | OneToOneField | Зв'язок з User |
| `bio` | TextField | Опис профілю (до 500 символів) |
| `avatar` | ImageField | Фото профілю |
| `avatar_color` | CharField | HEX колір аватара-заглушки |

### `Note`
Завдання користувача з пріоритетом.

| Поле | Тип | Опис |
|------|-----|------|
| `user` | ForeignKey | Власник завдання |
| `title` | CharField | Заголовок |
| `content` | TextField | Деталі |
| `done` | BooleanField | Виконано |
| `priority` | CharField | `low` / `medium` / `high` |
| `created_at` | DateTimeField | Дата створення |

### `Message`
Внутрішнє повідомлення між користувачами.

| Поле | Тип | Опис |
|------|-----|------|
| `sender` | ForeignKey | Відправник |
| `recipient` | ForeignKey | Отримувач |
| `subject` | CharField | Тема |
| `body` | TextField | Текст |
| `is_read` | BooleanField | Прочитано |
| `created_at` | DateTimeField | Дата |

---

## URL маршрути

| URL | Назва | Опис |
|-----|-------|------|
| `/` | `home` | Головна сторінка |
| `/register/` | `register` | Реєстрація |
| `/login/` | `login` | Вхід |
| `/logout/` | `logout` | Вихід |
| `/dashboard/` | `dashboard` | Дашборд |
| `/profile/` | `profile` | Мій профіль |
| `/notes/` | `notes` | Завдання |
| `/notes/<pk>/toggle/` | `note_toggle` | Позначити виконаним |
| `/notes/<pk>/delete/` | `note_delete` | Видалити завдання |
| `/messages/` | `messages_inbox` | Вхідні повідомлення |
| `/messages/<pk>/` | `message_read` | Читання повідомлення |

---

## Встановлення та запуск

```bash
# 1. Клонувати репозиторій
git clone https://github.com/VolodymyrMishchenko98/МійChat.git
cd МійChat

# 2. Створити та активувати venv
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Встановити залежності
pip install django==6.0.6 pillow

# 4. Застосувати міграції
cd parsing
python manage.py migrate

# 5. Створити суперкористувача (опційно)
python manage.py createsuperuser

# 6. Зібрати статику
python manage.py collectstatic

# 7. Запустити сервер
python manage.py runserver
```

Відкрити у браузері: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Дизайн

Мінімалістичний SaaS-стиль без зовнішніх CSS-фреймворків.

- **Палітра:** білий `#ffffff`, світло-сірий фон `#f9f9f7`, акцент індиго `#4f6ef7`
- **Типографія:** Inter (Google Fonts), ваги 400/500
- **Без:** градієнтів, тіней, border-radius > 12px
- **Sidebar:** фіксована, 220px, біла з навігацією
- **Topbar:** sticky, логотип + назва сторінки + профіль

---

## Автор

**Volodymyr Mishchenko** — [@VolodymyrMishchenko98](https://github.com/VolodymyrMishchenko98)
