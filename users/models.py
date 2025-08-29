from django.db import models
from django.core.validators import MinValueValidator
import uuid

class Offre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Supabase met aussi un default now()
    updated_at = models.DateTimeField(auto_now=True)      # Le trigger Supabase met aussi à jour

    class Meta:
        db_table = "offres"
        managed = False  # IMPORTANT: ne pas laisser Django créer/modifier cette table
        indexes = [
            models.Index(fields=["active"], name="idx_offres_active"),
            models.Index(fields=["category"], name="idx_offres_category"),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="offres_price_check"),
            models.CheckConstraint(check=models.Q(stock__gte=0), name="offres_stock_check"),
        ]
        verbose_name = "Offre"
        verbose_name_plural = "Offres"

    def __str__(self):
        return self.title
