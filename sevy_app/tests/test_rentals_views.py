from django.test import TestCase, Client
from django.urls import reverse
from sevy_app.models import CustomUser, Car, Company, CarLike
import json

class RentalsAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user = CustomUser.objects.create_user(
            email='user@example.com', 
            password='password123',
        )
        
        self.company = Company.objects.create(
            host_name="Test Host",
            company_name="Test Company",
            phone_number="+250780000000"
        )
        
        self.car = Car.objects.create(
            companyid=self.company,
            name="Test Car",
            brand="Test Brand",
            description="Test Description",
            location_name="Kigali",
            location_lat=-1.9441,
            location_long=30.0619,
            price_per_day=50000.00,
        )

        self.get_car_url = reverse('get_car', kwargs={'car_id': self.car.car_id})
        self.like_url = reverse('like_car', kwargs={'car_id': self.car.car_id})
        self.unlike_url = reverse('unlike_car', kwargs={'car_id': self.car.car_id})
        self.get_all_url = reverse('get_all_cars')

    def test_get_car_with_company_data(self):
        response = self.client.get(self.get_car_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        car_data = data['body']
        self.assertEqual(car_data['car_id'], self.car.car_id)
        
        # Verify company data is embedded
        self.assertIn('company', car_data)
        self.assertIsNotNone(car_data['company'])
        self.assertEqual(car_data['company']['company_id'], self.company.company_id)
        self.assertEqual(car_data['company']['host_name'], "Test Host")
        self.assertEqual(car_data['company']['phone_number'], "+250780000000")

    def test_get_all_cars(self):
        response = self.client.get(self.get_all_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        self.assertTrue(len(data['body']) > 0)
        
    def test_like_and_unlike_car(self):
        payload = {"user_id": self.user.custom_id}
        
        # Like the car
        response = self.client.post(self.like_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CarLike.objects.filter(car=self.car, user=self.user).exists())
        
        # Unlike the car
        response = self.client.post(self.unlike_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CarLike.objects.filter(car=self.car, user=self.user).exists())
