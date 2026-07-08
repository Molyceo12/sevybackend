from django.test import TestCase
from django.contrib.auth import get_user_model
from sevy_app.models.user_info import UserInfo

User = get_user_model()

class CustomUserTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='normal@user.com', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email(self):
        with self.assertRaisesMessage(ValueError, 'The Email field must be set'):
            User.objects.create_user(email='', password='foo')

class UserInfoTests(TestCase):
    def test_create_user_info(self):
        user = User.objects.create_user(email='test@test.com', password='foo')
        user_info = UserInfo.objects.create(user=user, full_names='Test User')
        
        self.assertEqual(user_info.user, user)
        self.assertEqual(user_info.full_names, 'Test User')
        self.assertEqual(str(user_info), 'Test User')
