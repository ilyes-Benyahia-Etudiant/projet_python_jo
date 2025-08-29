from django.conf import settings
from supabase import create_client, Client
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Service pour gérer les interactions avec Supabase pour le catalogue de produits.
    Approche débutant avec gestion d'erreur simple.
    """
    
    def __init__(self):
        # Initialisation du client Supabase
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.user_table = "users"
        self.product_table = "products"

    # ---------------- Utilisateurs ----------------
    def ping_connection(self, table_name: Optional[str] = None) -> Dict:
        """Test de connexion à Supabase sur une table."""
        target_table = table_name or self.user_table
        try:
            resp = self.client.table(target_table).select("id").limit(1).execute()
            count_resp = self.client.table(target_table).select("*", count="exact").execute()
            return {
                "status": "success",
                "message": f"Connexion OK. Accès à la table '{target_table}' réussi.",
                "connected": True,
                "table_accessible": True,
                "url": settings.SUPABASE_URL,
                "table_name": target_table,
                "row_count": count_resp.count,
            }
        except Exception as e:
            logger.error(f"Erreur de ping Supabase sur la table {target_table}: {e}")
            return {
                "status": "error",
                "message": f"Erreur de connexion/accès à la table '{target_table}': {str(e)}",
                "connected": False,
                "table_accessible": False,
                "url": settings.SUPABASE_URL,
                "table_name": target_table,
            }

    def get_all_supabase_users(self) -> List[Dict]:
        """Récupère tous les utilisateurs Supabase."""
        try:
            response = self.client.table(self.user_table).select(
                "id,email,full_name,avatar_url,bio,role,provider,email_confirmed,created_at,updated_at,last_sign_in"
            ).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs Supabase: {e}")
            return []

    def create_supabase_user(self, user_data: Dict) -> Dict:
        try:
            response = self.client.table(self.user_table).insert(user_data).execute()
            return {
                "success": True,
                "data": response.data[0] if response.data else None,
                "message": "Utilisateur créé avec succès"
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            return {"success": False, "error": str(e), "message": "Erreur lors de la création de l'utilisateur"}

    def update_supabase_user(self, user_id: str, user_data: Dict) -> Dict:
        try:
            response = self.client.table(self.user_table).update(user_data).eq("id", user_id).execute()
            return {
                "success": True,
                "data": response.data[0] if response.data else None,
                "message": "Utilisateur mis à jour avec succès"
            }
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur {user_id}: {e}")
            return {"success": False, "error": str(e), "message": "Erreur lors de la mise à jour de l'utilisateur"}

    def delete_supabase_user(self, user_id: str) -> Dict:
        try:
            self.client.table(self.user_table).delete().eq("id", user_id).execute()
            return {"success": True, "message": "Utilisateur supprimé avec succès"}
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'utilisateur {user_id}: {e}")
            return {"success": False, "error": str(e), "message": "Erreur lors de la suppression de l'utilisateur"}

    def get_supabase_user_by_id(self, user_id: str) -> Optional[Dict]:
        try:
            response = self.client.table(self.user_table).select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur {user_id}: {e}")
            return None

    # ---------------- Produits ----------------
    def get_all_products(self) -> List[Dict]:
        try:
            response = self.client.table(self.product_table).select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des produits: {e}")
            return []

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        try:
            response = self.client.table(self.product_table).select("*").eq("id", product_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du produit {product_id}: {e}")
            return None

    def get_products_by_category(self, category: str) -> List[Dict]:
        try:
            response = self.client.table(self.product_table).select("*").eq("category", category).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des produits de la catégorie {category}: {e}")
            return []

    def search_products(self, query: str) -> List[Dict]:
        try:
            response = self.client.table(self.product_table).select("*").ilike("name", f"%{query}%").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de produits '{query}': {e}")
            return []

    def get_all_offres(self) -> List[Dict]:
        """
        Récupère toutes les offres depuis la table 'offres' (Supabase).
        """
        if not self.client:
            logger.error("Client Supabase non initialisé.")
            return []
        try:
            resp = self.client.table("offres").select("*").order("created_at", desc=True).execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des offres: {e}")
            return []

    def get_offre_by_id(self, offre_id: str) -> Optional[Dict]:
        """
        Récupère une offre par ID.
        """
        if not self.client:
            logger.error("Client Supabase non initialisé.")
            return None
        try:
            resp = self.client.table("offres").select("*").eq("id", offre_id).limit(1).execute()
            return (resp.data or [None])[0]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'offre {offre_id}: {e}")
            return None

    def create_offre(self, data: Dict) -> Dict:
        """
        Crée une offre. Champs attendus: title, price, description, image, category, stock, active
        """
        if not self.client:
            return {"success": False, "message": "Client Supabase non initialisé"}
        try:
            resp = self.client.table("offres").insert(data).execute()
            return {
                "success": True,
                "data": (resp.data or [None])[0],
                "message": "Offre créée avec succès",
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'offre: {e}")
            return {"success": False, "message": str(e)}

    def update_offre(self, offre_id: str, data: Dict) -> Dict:
        """
        Met à jour une offre par ID.
        """
        if not self.client:
            return {"success": False, "message": "Client Supabase non initialisé"}
        try:
            resp = self.client.table("offres").update(data).eq("id", offre_id).execute()
            return {
                "success": True,
                "data": (resp.data or [None])[0],
                "message": "Offre mise à jour avec succès",
            }
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'offre {offre_id}: {e}")
            return {"success": False, "message": str(e)}

    def delete_offre(self, offre_id: str) -> Dict:
        """
        Supprime une offre par ID.
        """
        if not self.client:
            return {"success": False, "message": "Client Supabase non initialisé"}
        try:
            self.client.table("offres").delete().eq("id", offre_id).execute()
            return {"success": True, "message": "Offre supprimée avec succès"}
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'offre {offre_id}: {e}")
            return {"success": False, "message": str(e)}

# Instance globale du service pour l'admin
supabase_service = SupabaseService()
