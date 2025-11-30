# apps/products/managers.py
from django.db import models

class ProductManager(models.Manager):
    def active(self):
        """Return only active products (published)"""
        return self.filter(status='published')

    def available(self):
        """Return products that are in stock and published"""
        return self.filter(status='published', quantity__gt=0)

    def by_category(self, category_slug):
        """Return products by category slug"""
        return self.filter(category__slug=category_slug, status='published')

    def featured(self):
        """Return featured products"""
        return self.filter(is_featured=True, status='published')

    def bestsellers(self):
        """Return bestseller products"""
        return self.filter(is_bestseller=True, status='published')

    def new_arrivals(self):
        """Return new arrival products"""
        return self.filter(is_new=True, status='published')

    def low_stock(self):
        """Return products with low stock"""
        return self.filter(quantity__lte=models.F('low_stock_threshold'), track_quantity=True, status='published')