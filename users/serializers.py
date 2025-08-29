from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
import re

class RegisterInputSerializer(serializers.Serializer):
    # Serializer débutant, simple et explicite
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=True)  # Email requis pour permettre la connexion par email
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value):
        """
        Validation personnalisée du mot de passe avec des règles de sécurité renforcées
        """
        # Vérification de la longueur minimale
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        # Vérification de la présence d'au moins une lettre majuscule
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        
        # Vérification de la présence d'au moins une lettre minuscule
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
        
        # Vérification de la présence d'au moins un chiffre
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        # Vérification de la présence d'au moins un caractère spécial
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*...).")
        
        # Vérification qu'il ne contient pas d'espaces
        if ' ' in value:
            raise serializers.ValidationError("Le mot de passe ne doit pas contenir d'espaces.")
        
        # Utilisation des validateurs Django avec gestion d'erreur personnalisée
        try:
            validate_password(value)
        except ValidationError as e:
            # Traduction des messages d'erreur Django en français
            french_messages = []
            for error in e.messages:
                if "too common" in error.lower():
                    french_messages.append("Ce mot de passe est trop commun.")
                elif "entirely numeric" in error.lower():
                    french_messages.append("Le mot de passe ne peut pas être entièrement numérique.")
                elif "too similar" in error.lower():
                    french_messages.append("Le mot de passe est trop similaire à vos informations personnelles.")
                elif "too short" in error.lower():
                    french_messages.append("Ce mot de passe est trop court.")
                else:
                    french_messages.append(error)
            raise serializers.ValidationError(french_messages)
        
        return value

    def validate(self, attrs):
        # Vérifie que les mots de passe correspondent
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Les mots de passe ne correspondent pas."})
        
        # Validation de l'unicité de l'email (niveau débutant: on vérifie en amont sans changer le modèle)
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Un compte avec cet email existe déjà."})
        
        # Validation de l'unicité du nom d'utilisateur
        if User.objects.filter(username__iexact=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Ce nom d'utilisateur est déjà pris."})
        
        return attrs

    def create(self, validated_data):
        # Crée un utilisateur Django avec un mot de passe haché
        email = validated_data.get("email", "")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginInputSerializer(serializers.Serializer):
    # Utiliser email plutôt que username
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserOutputSerializer(serializers.ModelSerializer):
    # Sérialise les infos publiques de l'utilisateur
    is_staff = serializers.BooleanField(read_only=True)  # indique le rôle admin
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff"]