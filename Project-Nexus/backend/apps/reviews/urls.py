from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

router = DefaultRouter()
router.register('reviews', views.ProductReviewViewSet, basename='reviews')
router.register('admin/reviews', views.AdminReviewViewSet, basename='admin-reviews')

urlpatterns = [
    path('', include(router.urls)),
]



