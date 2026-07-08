from django.test import TestCase
from django.contrib.auth import get_user_model
from sevy_app.serializers.user import CustomerRegistrationSerializer
from sevy_app.models.user_info import UserInfo

User = get_user_model()

class CustomerRegistrationSerializerTests(TestCase):
    def test_valid_serializer(self):
        data = {
            'email': 'valid@test.com',
            'password': 'strongpassword',
            'fullname': 'Valid User'
        }
        serializer = CustomerRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserInfo.objects.count(), 1)
        self.assertEqual(user.email, 'valid@test.com')
        self.assertEqual(user.user_info.full_names, 'Valid User')

    def test_missing_fields(self):
        serializer = CustomerRegistrationSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('password', serializer.errors)
        self.assertIn('fullname', serializer.errors)

    def test_duplicate_email(self):
        User.objects.create_user(email='dup@test.com', password='foo')
        data = {
            'email': 'dup@test.com',
            'password': 'bar',
            'fullname': 'Another User'
        }
        serializer = CustomerRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertEqual(str(serializer.errors['email'][0]), "A user with this email already exists.")
