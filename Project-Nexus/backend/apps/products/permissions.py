from django.db import models

# In your Product model
class Product(models.Model):
    # ... your fields ...
    
    class Meta:
        permissions = [
            ("can_manage_products", "Can create, update, and delete products"),
            ("can_view_analytics", "Can view product analytics"),
            ("can_manage_inventory", "Can manage product inventory"),
        ]