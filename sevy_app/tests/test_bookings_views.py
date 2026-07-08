from django.test import TestCase, Client
from django.urls import reverse
from sevy_app.models import CustomUser, Driver, Car, Company, CarBooking
import json

class BookingsAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Set up a test customer
        self.customer = CustomUser.objects.create_user(
            email='customer@example.com', 
            password='password123',
        )
        self.customer.is_active = True
        self.customer.save()
        
        # Set up a company
        self.company = Company.objects.create(
            host_name="Test Host",
            company_name="Test Company"
        )
        
        # Set up a car
        self.car = Car.objects.create(
            companyid=self.company,
            name="Test Car",
            brand="Test Brand",
            price_per_day=50000.00,
        )
        
        # Set up a test driver
        self.driver_user = CustomUser.objects.create_user(
            email='driver@example.com',
            password='password123',
            user_type='driver'
        )
        self.driver_user.is_active = True
        self.driver_user.save()
        
        self.driver = Driver.objects.create(
            userid=self.driver_user,
            full_name='Test Driver',
            vehicle_make_color='Toyota White',
            plate_number='RAB123'
        )

        # Booking API endpoint
        self.create_url = reverse('create_booking')

    def test_create_self_drive_booking(self):
        payload = {
            "userid": self.customer.custom_id,
            "car_id": self.car.car_id,
            "booking_type": "self_drive",
            "rental_plan": "daily",
            "start_date": "2026-07-10T10:00:00Z",
            "end_date": "2026-07-15T10:00:00Z",
            "pickup_location": "Airport",
            "dropoff_location": "Hotel",
            "total_price": 250000.00
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertTrue(response_data['status'])
        
        booking_id = response_data['body']['booking_id']
        booking = CarBooking.objects.get(booking_id=booking_id)
        
        self.assertEqual(booking.car, self.car)
        self.assertEqual(booking.user, self.customer)
        self.assertIsNone(booking.driver)
        self.assertEqual(booking.booking_type, 'self_drive')
        self.assertEqual(float(booking.total_price), 250000.00)

    def test_create_with_driver_booking(self):
        payload = {
            "userid": self.customer.custom_id,
            "car_id": self.car.car_id,
            "driverid": self.driver_user.custom_id,
            "booking_type": "with_driver",
            "preferred_driver_gender": "female",
            "rental_plan": "daily",
            "start_date": "2026-07-10T10:00:00Z",
            "end_date": "2026-07-15T10:00:00Z",
            "pickup_location": "Airport",
            "dropoff_location": "Hotel",
            "total_price": 300000.00
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertTrue(response_data['status'])
        
        booking_id = response_data['body']['booking_id']
        booking = CarBooking.objects.get(booking_id=booking_id)
        
        self.assertEqual(booking.driver, self.driver)
        self.assertEqual(booking.preferred_driver_gender, 'female')

    def test_create_booking_missing_fields(self):
        payload = {
            "userid": self.customer.custom_id,
            # Missing car_id
            "booking_type": "self_drive",
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['status'])
        
    def test_create_booking_invalid_user(self):
        payload = {
            "userid": "invalid_id",
            "car_id": self.car.car_id,
            "booking_type": "self_drive",
            "rental_plan": "daily",
            "start_date": "2026-07-10T10:00:00Z",
            "end_date": "2026-07-15T10:00:00Z",
            "pickup_location": "Airport",
            "dropoff_location": "Hotel",
            "total_price": 250000.00
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['status'])

    def test_get_booking_details(self):
        # Create a booking manually
        booking = CarBooking.objects.create(
            user=self.customer,
            car=self.car,
            booking_type='self_drive',
            rental_plan='daily',
            start_date="2026-07-10T10:00:00Z",
            end_date="2026-07-15T10:00:00Z",
            pickup_location="Airport",
            dropoff_location="Hotel",
            total_price=250000.00,
            status='pending',
            payment_status='unpaid'
        )
        
        details_url = reverse('get_booking_details')
        payload = {"booking_id": booking.booking_id}
        
        response = self.client.post(details_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        body = data['body']
        self.assertEqual(body['booking_id'], booking.booking_id)
        self.assertEqual(body['userid'], self.customer.custom_id)
        self.assertEqual(body['car']['car_id'], self.car.car_id)
        self.assertEqual(body['total_price'], 250000.00)

    def test_get_booking_details_missing(self):
        details_url = reverse('get_booking_details')
        response = self.client.post(details_url, data=json.dumps({"booking_id": "missing"}), content_type='application/json')
        self.assertEqual(response.status_code, 404)
