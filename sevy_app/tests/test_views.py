from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerRegistrationViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('register-customer')

    def test_register_success(self):
        data = {
            'email': 'api@test.com',
            'password': 'password123',
            'fullname': 'API User'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Customer registered successfully.')
        self.assertEqual(response.data['body']['email'], 'api@test.com')

    def test_register_missing_data(self):
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertFalse(response.data['status'])
        self.assertIn('Email', response.data['message'])
        self.assertIn('Password', response.data['message'])
        self.assertIn('Fullname', response.data['message'])
        self.assertEqual(response.data['body'], {})

class DriverRegistrationViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('register-driver')

    def test_register_driver_success(self):
        data = {
            'email': 'driver_api@test.com',
            'password': 'password123',
            'fullname': 'API Driver',
            'vehicle_make_color': 'Nissan Black',
            'plate_number': 'RAC456B',
            'phone_number': '0781234567'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Driver registered successfully.')
        self.assertEqual(response.data['body']['email'], 'driver_api@test.com')
        
        # Verify database
        user = User.objects.get(email='driver_api@test.com')
        self.assertEqual(user.user_type, 'driver')
        self.assertTrue(hasattr(user, 'user_info'))
        
        from sevy_app.models import Driver
        driver = Driver.objects.get(userid=user)
        self.assertEqual(driver.full_name, 'API Driver')
        self.assertEqual(driver.vehicle_make_color, 'Nissan Black')
        self.assertEqual(driver.plate_number, 'RAC456B')

    def test_register_driver_missing_data(self):
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertFalse(response.data['status'])
        self.assertIn('Email', response.data['message'])
        self.assertIn('Password', response.data['message'])
        self.assertIn('Fullname', response.data['message'])
        self.assertIn('Vehicle_make_color', response.data['message'])
        self.assertIn('Plate_number', response.data['message'])
        self.assertEqual(response.data['body'], {})

class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(email='login@test.com', password='password123', user_type='customer')

    def test_login_success(self):
        data = {
            'email': 'login@test.com',
            'password': 'password123'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Login successful.')
        self.assertIn('tokens', response.data['body'])
        self.assertIn('access', response.data['body']['tokens'])
        self.assertIn('refresh', response.data['body']['tokens'])

    def test_login_missing_data(self):
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['message'], 'Email and password are required.')

    def test_login_invalid_credentials(self):
        data = {
            'email': 'login@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 401)
        self.assertFalse(response.data['status'])
        self.assertEqual(response.data['message'], 'Invalid email or password.')
