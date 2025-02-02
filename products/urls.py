from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, ProductByCategoryView, ProductListViewSet

app_name="products"

router = DefaultRouter()
router.register(r'admin', ProductViewSet, basename='product-detail')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'list', ProductListViewSet, basename='all-products')

urlpatterns = [
    path('', include(router.urls)),
    path('by-category/<int:category_id>/', ProductByCategoryView.as_view(), name='products_by_category'),
]
