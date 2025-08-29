from django.db import models
from decimal import Decimal

class Product(models.Model):
    """
    Modèle représentant un produit du catalogue.
    Note: Les données sont stockées dans Supabase, ce modèle sert principalement 
    pour la validation et la structure des données côté Django.
    """
    
    # Champs correspondant à la structure Supabase
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    image_url = models.URLField(verbose_name="URL de l'image", blank=True, null=True)
    stock_quantity = models.IntegerField(verbose_name="Quantité en stock", default=0)
    is_active = models.BooleanField(verbose_name="Produit actif", default=True)
    
    # Métadonnées Django
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock."""
        return self.stock_quantity > 0
