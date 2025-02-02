from rest_framework.viewsets import mixins, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from .models import Product, Category, ProductCategory
from .serializers import ProductSerializer, CategorySerializer


class ProductListViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by("created_at")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductByCategoryView(APIView):
    def get(self, request, category_id, *args, **kwargs):
        category = Category.objects.get(id=category_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        product_categories = ProductCategory.objects.filter(category=category)
        products = Product.objects.filter(
            id__in=product_categories.values("product_id")
        )
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class IsAdminOrShopAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True

        if request.user.is_authenticated and request.user.role in [
            "admin",
            "shop_admin",
        ]:
            return True

        return False


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrShopAdmin]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Product.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
