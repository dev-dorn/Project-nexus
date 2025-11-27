from django.test import TestCase
from django.urls import reverse

class BasicTests(TestCase):
    def test_home_page_status(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_login_page(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)