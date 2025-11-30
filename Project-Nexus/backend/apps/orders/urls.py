from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders'

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='orders')
router.register('order-items', views.OrderItemViewSet, basename='order-items')
router.register('shipping-methods', views.ShippingMethodViewSet, basename='shipping-methods')
router.register('admin/orders', views.AdminOrderViewSet, basename='admin-orders')

urlpatterns = [
    path('', include(router.urls)),
]