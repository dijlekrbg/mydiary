
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class SimpleTest(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)



class HomePageTest(TestCase):
    def test_homepage_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class DiaryEntryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_diary_list_requires_login(self):
        response = self.client.get(reverse('diary_list'))
        self.assertEqual(response.status_code, 302)  

    def test_diary_list_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('diary_list'))
        self.assertEqual(response.status_code, 200)