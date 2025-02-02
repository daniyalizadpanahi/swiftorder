from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import CartViewSet, CartItemViewSet, OrderViewSet

app_name = "orders"

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")
router.register("carts", CartViewSet, basename="carts")

carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_router.register("items", CartItemViewSet, basename="cart-items")

urlpatterns = router.urls + carts_router.urls
