from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import BasePagination
from .models import Product, Category, ProductCategory
from .serializers import ProductSerializer, CategorySerializer


class ProductListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductByCategoryView(APIView):
    def get(self, request, category_id, *args, **kwargs):
        category = Category.objects.get(id=category_id)
        products = Product.objects.filter(categories=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class IsAdminOrShopAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ["admin", "shop_admin"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrShopAdmin]
    pagination_class = BasePagination

    def get_queryset(self):
        return Product.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
