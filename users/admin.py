from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib import messages
from catalog.supabase_service import supabase_service
from datetime import datetime
from .models import Offre
import os

# -----------------------
# Admin personnalisé pour les utilisateurs Supabase
# -----------------------
class CustomUserAdmin(BaseUserAdmin):
    change_list_template = "admin/auth/user/supabase_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('extract-supabase-users/', 
                 self.admin_site.admin_view(self.extract_supabase_users_view),
                 name='extract_supabase_users'),
            path('add-supabase/', 
                 self.admin_site.admin_view(self.add_supabase_user_view),
                 name='add_supabase_user'),
            path('<str:user_id>/edit-supabase/', 
                 self.admin_site.admin_view(self.edit_supabase_user_view),
                 name='edit_supabase_user'),
            path('<str:user_id>/delete-supabase/', 
                 self.admin_site.admin_view(self.delete_supabase_user_view),
                 name='delete_supabase_user'),
        ]
        return custom_urls + urls

    def extract_supabase_users_view(self, request):
        if request.method == 'GET':
            supabase_users = supabase_service.get_all_supabase_users()
            context = {
                'title': 'Extraction des utilisateurs Supabase',
                'supabase_users': supabase_users,
                'users_count': len(supabase_users),
                'opts': self.model._meta,
                'has_view_permission': True,
            }
            return render(request, 'admin/users/supabase_users_extract.html', context)

    def add_supabase_user_view(self, request):
        if request.method == 'POST':
            user_data = {
                'email': request.POST.get('email'),
                'full_name': request.POST.get('full_name', ''),
                'role': request.POST.get('role', 'user'),
                'provider': request.POST.get('provider', 'email'),
                'email_confirmed': request.POST.get('email_confirmed') == 'on',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            result = supabase_service.create_supabase_user(user_data)
            if result['success']:
                messages.success(request, result['message'])
                return redirect('admin:auth_user_changelist')
            messages.error(request, result.get('message') or result.get('error'))
        context = {'title': 'Ajouter un utilisateur Supabase', 'opts': self.model._meta}
        return render(request, 'admin/users/add_supabase_user.html', context)

    def edit_supabase_user_view(self, request, user_id):
        user = supabase_service.get_supabase_user_by_id(user_id)
        if not user:
            messages.error(request, "Utilisateur non trouvé")
            return redirect('admin:auth_user_changelist')
        if request.method == 'POST':
            user_data = {
                'email': request.POST.get('email'),
                'full_name': request.POST.get('full_name', ''),
                'role': request.POST.get('role', 'user'),
                'provider': request.POST.get('provider', 'email'),
                'email_confirmed': request.POST.get('email_confirmed') == 'on',
                'updated_at': datetime.now().isoformat()
            }
            result = supabase_service.update_supabase_user(user_id, user_data)
            if result['success']:
                messages.success(request, result['message'])
                return redirect('admin:auth_user_changelist')
            messages.error(request, result.get('message') or result.get('error'))
        context = {'title': f"Modifier l'utilisateur {user.get('email', '')}",
                   'user': user, 'opts': self.model._meta}
        return render(request, 'admin/users/edit_supabase_user.html', context)

    def delete_supabase_user_view(self, request, user_id):
        user = supabase_service.get_supabase_user_by_id(user_id)
        if not user:
            messages.error(request, "Utilisateur non trouvé")
            return redirect('admin:auth_user_changelist')
        if request.method == 'POST':
            result = supabase_service.delete_supabase_user(user_id)
            if result['success']:
                messages.success(request, result['message'])
            else:
                messages.error(request, result.get('message') or result.get('error'))
            return redirect('admin:auth_user_changelist')
        context = {'title': f"Supprimer l'utilisateur {user.get('email', '')}",
                   'user': user, 'opts': self.model._meta}
        return render(request, 'admin/users/delete_supabase_user.html', context)

    def get_queryset(self, request):
        return User.objects.none()

    def has_add_permission(self, request): return True
    def has_change_permission(self, request, obj=None): return True
    def has_delete_permission(self, request, obj=None): return True

    def changelist_view(self, request, extra_context=None):
        supabase_users = supabase_service.get_all_supabase_users()
        extra_context = extra_context or {}
        extra_context.update({
            'extract_supabase_url': reverse('admin:extract_supabase_users'),
            'add_supabase_url': reverse('admin:add_supabase_user'),
            'supabase_users': supabase_users,
            'users_count': len(supabase_users),
            'title': 'Utilisateurs (Supabase)',
        })
        return super().changelist_view(request, extra_context)

# Désenregistrer l'admin par défaut et enregistrer le nôtre
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# -----------------------
# Admin pour les Offres Supabase
# -----------------------
@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "active", "stock", "category", "created_at")
    list_filter = ("active", "category", "created_at")
    search_fields = ("title", "description", "category")
    change_list_template = "admin/users/offres_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-offre/', self.admin_site.admin_view(self.add_offre_view), name='add_offre'),
            path('<str:offre_id>/edit-offre/', self.admin_site.admin_view(self.edit_offre_view), name='edit_offre'),
            path('<str:offre_id>/delete-offre/', self.admin_site.admin_view(self.delete_offre_view), name='delete_offre'),
        ]
        return custom_urls + urls

    def get_queryset(self, request):
        # Ne requête pas la DB (router -> Postgres/Supabase).
        # On affichera via le template avec les données Supabase.
        return Offre.objects.none()

    def changelist_view(self, request, extra_context=None):
        offres = []
        try:
            offres = supabase_service.get_all_offres()
            if not offres:
                messages.info(request, "Aucune offre trouvée ou connexion Supabase indisponible.")
        except Exception as e:
            messages.error(request, f"Erreur de connexion Supabase: {e}")
        extra_context = extra_context or {}
        extra_context.update({
            "offres": offres,
            "offres_count": len(offres or []),
            "title": "Offres (Supabase)",
            "add_offre_url": reverse("admin:add_offre"),
        })
        return super().changelist_view(request, extra_context)

    def has_module_permission(self, request):
        # Toujours afficher le module pour permettre un message explicite sur la page
        return True

    def has_add_permission(self, request): return True
    def has_change_permission(self, request, obj=None): return True
    def has_delete_permission(self, request, obj=None): return True

    # --- Vues personnalisées ---
    def add_offre_view(self, request):
        if request.method == "POST":
            data = {
                "title": request.POST.get("title") or "",
                "price": request.POST.get("price") or 0,
                "description": request.POST.get("description") or "",
                "image": request.POST.get("image") or "",
                "category": request.POST.get("category") or "",
                "stock": int(request.POST.get("stock") or 0),
                "active": request.POST.get("active") == "on",
            }
            result = supabase_service.create_offre(data)
            if result.get("success"):
                messages.success(request, result.get("message", "Offre créée"))
                return redirect("admin:users_offre_changelist")
            messages.error(request, result.get("message") or "Erreur lors de la création")
        context = {
            "title": "Ajouter une offre",
            "opts": self.model._meta,
        }
        return render(request, "admin/users/add_offre.html", context)

    def edit_offre_view(self, request, offre_id: str):
        offre = supabase_service.get_offre_by_id(offre_id)
        if not offre:
            messages.error(request, "Offre non trouvée")
            return redirect("admin:users_offre_changelist")
        if request.method == "POST":
            data = {
                "title": request.POST.get("title") or "",
                "price": request.POST.get("price") or 0,
                "description": request.POST.get("description") or "",
                "image": request.POST.get("image") or "",
                "category": request.POST.get("category") or "",
                "stock": int(request.POST.get("stock") or 0),
                "active": request.POST.get("active") == "on",
            }
            result = supabase_service.update_offre(offre_id, data)
            if result.get("success"):
                messages.success(request, result.get("message", "Offre mise à jour"))
                return redirect("admin:users_offre_changelist")
            messages.error(request, result.get("message") or "Erreur lors de la mise à jour")
        context = {
            "title": f"Modifier l'offre {offre.get('title', '')}",
            "offre": offre,
            "opts": self.model._meta,
        }
        return render(request, "admin/users/edit_offre.html", context)

    def delete_offre_view(self, request, offre_id: str):
        offre = supabase_service.get_offre_by_id(offre_id)
        if not offre:
            messages.error(request, "Offre non trouvée")
            return redirect("admin:users_offre_changelist")
        if request.method == "POST":
            result = supabase_service.delete_offre(offre_id)
            if result.get("success"):
                messages.success(request, result.get("message", "Offre supprimée"))
            else:
                messages.error(request, result.get("message") or "Erreur lors de la suppression")
            return redirect("admin:users_offre_changelist")
        context = {
            "title": f"Supprimer l'offre {offre.get('title', '')}",
            "offre": offre,
            "opts": self.model._meta,
        }
        return render(request, "admin/users/delete_offre.html", context)
