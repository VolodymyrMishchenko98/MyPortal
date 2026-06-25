from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notes/', views.notes_view, name='notes'),
    path('notes/<int:pk>/toggle/', views.note_toggle, name='note_toggle'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('messages/', views.messages_inbox, name='messages_inbox'),
    path('messages/<int:pk>/', views.message_read, name='message_read'),
]
