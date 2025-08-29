from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    RegisterInputSerializer,
    LoginInputSerializer,
    UserOutputSerializer,
)
from django.contrib.auth.models import User
from catalog.supabase_service import supabase_service  # <-- ajout import du service Supabase

# Create your views here.

@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Cette vue force l'envoi du cookie CSRF au client.
    - Le front doit d'abord appeler /api/auth/csrf/ (GET) pour recevoir le cookie 'csrftoken'.
    - Ensuite, sur les requêtes POST, inclure le header 'X-CSRFToken' avec cette valeur.
    """
    return Response({"detail": "CSRF cookie set."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur.
    - Validation débutant via RegisterInputSerializer.
    - Création de l'utilisateur Django (mot de passe haché).
    """
    serializer = RegisterInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    # Tentative: miroir dans Supabase (optionnel)
    try:
        supabase_payload = {
            "email": user.email,
            "full_name": user.username,  # adapte si tu as un champ 'full_name' dans ta table Supabase
            "role": "user",
            "provider": "email",
            "email_confirmed": False,
        }
        supabase_service.create_supabase_user(supabase_payload)
    except Exception:
        # On n'échoue pas l'inscription Django si Supabase échoue
        pass

    return Response(
        {
            "detail": "Inscription réussie.",
            "user": UserOutputSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Connexion par session via email + mot de passe.
    - On recherche l'utilisateur par son email (insensible à la casse).
    - On authentifie via authenticate() en passant son username interne + mot de passe.
    - CONTRÖLE DU RÖLE ET REDIRECTION:
        * user.is_staff == True => admin => redirect_url = '/admin/'
        * sinon => utilisateur => redirect_url = '/'
      Le front lit redirect_url et effectue la redirection.
    """
    serializer = LoginInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    # Recherche par email (cas d'erreur si plusieurs comptes partagent le même email)
    users_with_email = User.objects.filter(email__iexact=email)
    if not users_with_email.exists():
        return Response({"detail": "Email ou mot de passe invalide."}, status=status.HTTP_400_BAD_REQUEST)
    if users_with_email.count() > 1:
        return Response({"detail": "Plusieurs comptes utilisent cet email. Contactez le support."}, status=status.HTTP_400_BAD_REQUEST)

    user_obj = users_with_email.first()
    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        return Response({"detail": "Email ou mot de passe invalide."}, status=status.HTTP_400_BAD_REQUEST)

    django_login(request, user)

    # Contrôle du rôle et redirection
    redirect_url = "/admin/" if user.is_staff else "/user/"  # <-- Non-admin vers l'espace utilisateur

    return Response(
        {
            "detail": "Connexion réussie.",
            "user": UserOutputSerializer(user).data,
            "redirect_url": redirect_url,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Déconnexion: supprime la session serveur de l'utilisateur connecté.
    """
    django_logout(request)
    return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Renvoie les informations de l'utilisateur connecté.
    - Utile pour vérifier l'état d'authentification côté front.
    """
    return Response(UserOutputSerializer(request.user).data, status=status.HTTP_200_OK)
