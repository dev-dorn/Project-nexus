import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    featured = django_filters.BooleanFilter(field_name='is_featured')
    bestseller = django_filters.BooleanFilter(field_name='is_bestseller')
    new = django_filters.BooleanFilter(field_name='is_new')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'min_price', 'max_price', 'featured', 'bestseller', 'new']