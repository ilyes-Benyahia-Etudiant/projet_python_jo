from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render

from .supabase_service import supabase_service
from .serializers import ProductSerializer, ProductListSerializer

# Nouvelle vue pour tester la connexion Supabase
@api_view(["GET"])
@permission_classes([AllowAny])
def ping_supabase(request):
    """
    Teste la connexion à Supabase en pingant la table spécifiée.
    Utilisation: /catalog/api/ping/?table=user
    Si aucun paramètre 'table' n'est fourni, par défaut 'user'.
    """
    table = request.GET.get("table") or "users"
    result = supabase_service.ping_connection(table)
    if result.get("connected"):
        return Response(result, status=status.HTTP_200_OK)
    return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# Vues API pour le catalogue
@api_view(["GET"])
@permission_classes([AllowAny])
def product_list(request):
    """
    Liste tous les produits du catalogue Supabase.
    Support de filtrage par catégorie et recherche.
    """
    try:
        # Paramètres de requête
        category = request.GET.get('category')
        search = request.GET.get('search')
        
        if search:
            products = supabase_service.search_products(search)
        elif category:
            products = supabase_service.get_products_by_category(category)
        else:
            products = supabase_service.get_all_products()
        
        # Sérialisation des données
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            "products": serializer.data,
            "count": len(products)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Erreur lors de la récupération des produits"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail(request, product_id):
    """
    Récupère les détails d'un produit spécifique.
    """
    try:
        product = supabase_service.get_product_by_id(product_id)
        
        if not product:
            return Response(
                {"error": "Produit non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Erreur lors de la récupération du produit"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([AllowAny])
def categories_list(request):
    """
    Récupère la liste des catégories disponibles.
    """
    try:
        products = supabase_service.get_all_products()
        categories = list(set(product.get('category', '') for product in products if product.get('category')))
        categories.sort()
        
        return Response({
            "categories": categories,
            "count": len(categories)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": "Erreur lors de la récupération des catégories"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Vues pour les templates HTML
@ensure_csrf_cookie
def catalog_page(request):
    """
    Page du catalogue de produits.
    """
    return render(request, 'catalog/catalog.html')

@ensure_csrf_cookie
def product_detail_page(request, product_id):
    """
    Page de détail d'un produit.
    """
    return render(request, 'catalog/product_detail.html', {'product_id': product_id})
