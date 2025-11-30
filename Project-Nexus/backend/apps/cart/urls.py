from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

router = DefaultRouter()
router.register('cart', views.CartViewSet, basename='cart')
router.register('cart-items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
]