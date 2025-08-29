document.addEventListener('DOMContentLoaded', function() {
    const productsContainer = document.getElementById('products-container');
    const loadingElement = document.getElementById('loading');
    const noProductsElement = document.getElementById('no-products');
    const categoryFilter = document.getElementById('category-filter');
    const searchInput = document.getElementById('search-input');
    
    let allProducts = [];
    let categories = [];

    // Initialisation
    init();

    async function init() {
        await loadCategories();
        await loadProducts();
        setupEventListeners();
    }

    async function loadCategories() {
        try {
            const response = await fetch('/api/categories/');
            const result = await response.json();
            
            if (response.ok) {
                categories = result.categories;
                populateCategoryFilter();
            }
        } catch (error) {
            console.error('Erreur lors du chargement des catégories:', error);
        }
    }

    async function loadProducts(category = '', search = '') {
        showLoading(true);
        
        try {
            let url = '/api/products/';
            const params = new URLSearchParams();
            
            if (category) params.append('category', category);
            if (search) params.append('search', search);
            
            if (params.toString()) {
                url += '?' + params.toString();
            }

            const response = await fetch(url);
            const result = await response.json();

            if (response.ok) {
                allProducts = result.products;
                displayProducts(allProducts);
            } else {
                showToast('Erreur lors du chargement des produits', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            showToast('Erreur de connexion au serveur', 'error');
        } finally {
            showLoading(false);
        }
    }

    function populateCategoryFilter() {
        categoryFilter.innerHTML = '<option value="">Toutes les catégories</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
    }

    function displayProducts(products) {
        productsContainer.innerHTML = '';
        
        if (products.length === 0) {
            noProductsElement.classList.remove('d-none');
            return;
        }
        
        noProductsElement.classList.add('d-none');
        
        products.forEach(product => {
            const productCard = createProductCard(product);
            productsContainer.appendChild(productCard);
        });
    }

    function createProductCard(product) {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-sm-6 mb-4';
        
        const stockBadge = product.stock_quantity > 0 
            ? `<span class="badge bg-success">En stock (${product.stock_quantity})</span>`
            : '<span class="badge bg-danger">Rupture de stock</span>';
        
        col.innerHTML = `
            <div class="card h-100">
                ${product.image_url ? 
                    `<img src="${product.image_url}" class="card-img-top" alt="${product.name}" style="height: 200px; object-fit: cover;">` :
                    '<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;"><span class="text-muted">Pas d\'image</span></div>'
                }
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${product.name}</h5>
                    <p class="card-text flex-grow-1">${product.description || 'Aucune description disponible'}</p>
                    <div class="mt-auto">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="h5 mb-0 text-primary">${product.price} €</span>
                            ${stockBadge}
                        </div>
                        <small class="text-muted">Catégorie: ${product.category}</small>
                        <div class="mt-2">
                            <a href="/product/${product.id}/" class="btn btn-outline-primary btn-sm me-2">Voir détails</a>
                            ${product.stock_quantity > 0 ? 
                                `<button class="btn btn-primary btn-sm" onclick="addToCart(${product.id})">Ajouter au panier</button>` :
                                '<button class="btn btn-secondary btn-sm" disabled>Indisponible</button>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return col;
    }

    function setupEventListeners() {
        // Filtre par catégorie
        categoryFilter.addEventListener('change', function() {
            const category = this.value;
            const search = searchInput.value.trim();
            loadProducts(category, search);
        });

        // Recherche avec délai
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const search = this.value.trim();
            const category = categoryFilter.value;
            
            searchTimeout = setTimeout(() => {
                loadProducts(category, search);
            }, 500); // Délai de 500ms
        });
    }

    function showLoading(show) {
        if (show) {
            loadingElement.style.display = 'block';
            productsContainer.style.display = 'none';
            noProductsElement.classList.add('d-none');
        } else {
            loadingElement.style.display = 'none';
            productsContainer.style.display = 'flex';
        }
    }

    // Fonction globale pour ajouter au panier
    window.addToCart = function(productId) {
        // Cette fonction sera implémentée avec le système de panier
        showToast('Fonctionnalité panier à venir', 'info');
    };
});