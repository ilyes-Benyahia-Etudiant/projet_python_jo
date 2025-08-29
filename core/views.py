from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

@ensure_csrf_cookie
def home_page(request):
    """
    Page d'accueil simple.
    Dépose aussi un cookie CSRF (grâce à ensure_csrf_cookie) pour les requêtes API.
    """
    return render(request, "home.html")

@ensure_csrf_cookie
def login_page(request):
    """
    Page de connexion HTML.
    Elle utilise fetch() pour appeler l'API /api/auth/login/ sans rechargement.
    Le cookie CSRF est déposé si absent.
    """
    return render(request, "auth/login.html")

@ensure_csrf_cookie
def register_page(request):
    """
    Page d'inscription HTML.
    Elle utilise fetch() pour appeler l'API /api/auth/register/ sans rechargement.
    Le cookie CSRF est déposé si absent.
    """
    return render(request, "auth/register.html")

@ensure_csrf_cookie
@login_required
def user_page(request):
    """
    Page HTML de l'espace utilisateur.
    - Requiert une session connectée (login_required).
    - Dépose un cookie CSRF si absent (ensure_csrf_cookie) pour les appels API depuis le template.
    - Le contenu détaillé (infos utilisateur) est récupéré via /api/auth/me côté JS.
    """
    return render(request, "user/dashboard.html")