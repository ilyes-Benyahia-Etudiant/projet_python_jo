from django.urls import path
from . import views

urlpatterns = [
    path("csrf/", views.get_csrf_token, name="auth_csrf"),
    path("register/", views.register, name="auth_register"),
    path("login/", views.login, name="auth_login"),
    path("logout/", views.logout, name="auth_logout"),
    path("me/", views.me, name="auth_me"),
]