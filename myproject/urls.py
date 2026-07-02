"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('notes/', views.notes, name='notes'),
    path('notes/add/', views.add_note, name='add_note'),
    path('notes/toggle/<int:note_id>/', views.toggle_note, name='toggle_note'),
    path('notes/delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/new/', views.messages_new, name='messages_new'),
    path('messages/<str:username>/', views.messages_thread, name='messages_thread'),
    path('account/delete/', views.delete_account, name='delete_account'),
]