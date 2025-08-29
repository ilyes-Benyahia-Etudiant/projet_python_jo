from django.urls import path  # Import correct du module path
from . import views          # Import des vues du module courant

urlpatterns = [             # Liste contenant toutes les routes
    # API endpoints
    path('api/ping/', views.ping_supabase, name='ping_supabase'),
    path('api/products/', views.product_list, name='product_list'),
    path('api/products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/categories/', views.categories_list, name='categories_list'),
    
    # Pages HTML
    path('catalog/', views.catalog_page, name='catalog_page'),
    path('product/<int:product_id>/', views.product_detail_page, name='product_detail_page'),
]