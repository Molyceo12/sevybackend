from django.test import TestCase, Client
from django.urls import reverse
from sevy_app.models import CustomUser, UserInfo, Trip, CarBooking, Transaction, Notification, Car, Driver
import json

class GetUserAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create user
        self.customer = CustomUser.objects.create_user(
            email='testcustomer@example.com', 
            password='password123',
            user_type='customer'
        )
        
        # Create UserInfo
        self.user_info = UserInfo.objects.create(
            user=self.customer,
            full_names="Test Customer Name"
        )
        
        # Create mock driver
        self.driver_user = CustomUser.objects.create_user(
            email='driver@example.com',
            password='password123',
            user_type='driver'
        )
        self.driver = Driver.objects.create(
            userid=self.driver_user,
            full_name='Test Driver',
            vehicle_make_color='Toyota White',
            plate_number='RAB123'
        )
        
        # Create 2 Trips
        Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            estimated_time="15 mins",
            total_price=5000.00,
            status="completed"
        )
        Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            estimated_time="20 mins",
            total_price=7000.00,
            status="completed"
        )
        
        from sevy_app.models import Company
        self.company = Company.objects.create(
            host_name="Test Host",
            company_name="Test Company"
        )
        
        # Create 1 Car and 1 Booking
        self.car = Car.objects.create(
            name="Corolla",
            brand="Toyota",
            price_per_day=50000.00,
            companyid=self.company
        )
        CarBooking.objects.create(
            user=self.customer,
            car=self.car,
            booking_type='self_drive',
            rental_plan='daily',
            start_date="2026-07-10T10:00:00Z",
            end_date="2026-07-15T10:00:00Z",
            total_price=250000.00,
            status='confirmed',
            payment_status='paid'
        )
        
        # Create some completed transactions
        Transaction.objects.create(
            user=self.customer,
            amount=5000.00,
            transaction_type='trip',
            status='completed'
        )
        Transaction.objects.create(
            user=self.customer,
            amount=250000.00,
            transaction_type='car_booking',
            status='completed'
        )
        # Create a pending transaction (should not be counted)
        Transaction.objects.create(
            user=self.customer,
            amount=100000.00,
            transaction_type='trip',
            status='pending'
        )
        
        # Create 1 Notification
        Notification.objects.create(
            user=self.customer,
            title="Welcome",
            message="Welcome to Sevy",
            notification_type='system'
        )

        self.get_user_url = reverse('get_user')

    def test_get_user_success(self):
        payload = {"userid": self.customer.custom_id}
        response = self.client.post(self.get_user_url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['status'])
        
        body = data['body']
        
        # Verify the simple user fields
        self.assertEqual(body['userid'], self.customer.custom_id)
        self.assertEqual(body['email'], "testcustomer@example.com")
        self.assertEqual(body['names'], "Test Customer Name")
        
        # Verify math
        self.assertEqual(body['total_trips'], 2)
        self.assertEqual(body['total_bookings'], 1)
        self.assertEqual(body['total_money_spent'], 255000.00)  # 5000 + 250000 (pending 100k ignored)
        self.assertFalse(body.get('is_driver', True))

    def test_get_user_dashboard_as_driver(self):
        # Create driver profile for customer
        from sevy_app.models import Driver
        Driver.objects.create(
            userid=self.customer,
            full_name="Maurice Driver",
            vehicle_make_color="Toyota Red",
            plate_number="RAE123A",
            balance=150.50,
            bonus=20.00
        )
        
        # Create a transaction
        Transaction.objects.create(
            user=self.customer,
            amount=50.00,
            transaction_type='trip',
            status='completed'
        )
        
        url = reverse('get_user')
        payload = {"userid": self.customer.custom_id}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        body = response.json()['body']
        
        self.assertTrue(body['is_driver'])
        self.assertEqual(body['balance'], 150.50)
        self.assertEqual(body['bonus'], 20.00)
        self.assertEqual(len(body['transactions']), 4)
        # Verify the newly added one is first (descending order)
        self.assertEqual(body['transactions'][0]['amount'], 50.00)
        
        # Verify arrays
        self.assertEqual(len(body['trips']), 2)
        self.assertEqual(len(body['bookings']), 1)
        
        # Verify notifications
        self.assertEqual(len(body['notifications']), 1)
        self.assertEqual(body['notifications'][0]['title'], "Welcome")

    def test_get_user_not_found(self):
        payload = {"userid": "invalid_id"}
        response = self.client.post(self.get_user_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        
    def test_get_user_missing_id(self):
        payload = {}
        response = self.client.post(self.get_user_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_delete_account(self):
        url = reverse('delete_account')
        payload = {"userid": self.customer.custom_id}
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        # Verify the user is soft deleted
        from sevy_app.models import CustomUser
        user = CustomUser.objects.filter(custom_id=self.customer.custom_id).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_deleted)
        self.assertFalse(user.is_active)
        self.assertFalse(user.has_usable_password())
