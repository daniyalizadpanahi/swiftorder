from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, ProductByCategoryView, ProductListViewSet

app_name="products"

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'all-products', ProductListViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/products-by-category/<int:category_id>/', ProductByCategoryView.as_view(), name='products_by_category'),
]
