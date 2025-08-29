"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path('', core_views.home_page, name='home'),
    path('login/', core_views.login_page, name='login_page'),
    path('register/', core_views.register_page, name='register_page'),
    path('user/', core_views.user_page, name='user_page'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('', include('catalog.urls')),  # Inclure les URLs du catalogue
]
