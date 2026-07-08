from django.test import TestCase, Client
from django.urls import reverse
from sevy_app.models import CustomUser, Driver, Trip
import json

class TripAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.customer = CustomUser.objects.create_user(
            email='customer@example.com', 
            password='password123',
        )
        
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

        self.create_url = reverse('create_trip')
        self.details_url = reverse('get_trip_details')

    def test_create_trip_success(self):
        payload = {
            "userid": self.customer.custom_id,
            "driverid": self.driver_user.custom_id,
            "estimated_time": "15 mins",
            "total_price": 5000.00,
            "payment_method": "cash",
            "trip_distance_km": 12.5,
            "start_lat": -1.9441,
            "start_long": 30.0619,
            "start_place_name": "Kigali",
            "destination_lat": -1.9536,
            "destination_long": 30.0605,
            "destination_name": "Kacyiru"
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertTrue(response_data['status'])
        
        trip_id = response_data['body']['trip_id']
        trip = Trip.objects.get(trip_id=trip_id)
        
        self.assertEqual(trip.userid, self.customer)
        self.assertEqual(trip.driverid, self.driver)
        self.assertEqual(trip.trip_distance_km, 12.5)

    def test_create_trip_missing_fields(self):
        payload = {
            "userid": self.customer.custom_id,
            "estimated_time": "15 mins"
            # Missing total_price, coordinates, etc.
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_trip_details(self):
        # Create a trip manually
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            estimated_time="20 mins",
            total_price=6000.00,
            trip_distance_km=15.0,
            start_lat=-1.9441,
            start_long=30.0619,
            destination_lat=-1.9536,
            destination_long=30.0605,
        )
        
        payload = {"trip_id": trip.trip_id}
        response = self.client.post(self.details_url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['status'])
        
        self.assertEqual(data['body']['trip_id'], trip.trip_id)
        self.assertEqual(data['body']['userid'], self.customer.custom_id)
        self.assertEqual(data['body']['driverid'], self.driver_user.custom_id)
        self.assertEqual(data['body']['total_price'], 6000.00)
        self.assertEqual(data['body']['distance'], '15.0 km')

    def test_get_trip_details_invalid_id(self):
        payload = {"trip_id": "nonexistent"}
        response = self.client.post(self.details_url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        
    def test_get_driver_incoming_trips(self):
        # Create a matching trip
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            service_type='driver_and_car',
            driver_status='waiting',
            status='upcoming',
            estimated_time="20 mins"
        )
        # Create a non-matching trip
        Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            service_type='driver_only', # Wrong service type
            driver_status='waiting',
            status='upcoming',
            estimated_time="20 mins"
        )
        
        url = reverse('get_driver_incoming_trips')
        payload = {"driverid": self.driver_user.custom_id}
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        # Should only return the matching trip
        self.assertEqual(len(data['body']), 1)
        self.assertEqual(data['body'][0]['trip_id'], trip.trip_id)

    def test_update_driver_trip_status(self):
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            driver_status='waiting',
            status='upcoming',
            estimated_time="10 mins"
        )
        
        url = reverse('update_trip_status')
        payload = {
            "trip_id": trip.trip_id,
            "is_coming": True
        }
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        trip.refresh_from_db()
        self.assertEqual(trip.driver_status, 'coming')
        
    def test_update_driver_trip_status_rejected(self):
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            driver_status='waiting',
            status='upcoming',
            estimated_time="10 mins"
        )
        
        url = reverse('update_trip_status')
        payload = {
            "trip_id": trip.trip_id,
            "is_rejected": True
        }
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        trip.refresh_from_db()
        self.assertEqual(trip.driver_status, 'rejected')
        
    def test_update_driver_trip_status_invalid_status(self):
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            driver_status='waiting',
            status='upcoming',
            estimated_time="10 mins"
        )
        
        url = reverse('update_trip_status')
        payload = {
            "trip_id": trip.trip_id,
            "is_flying": True # Invalid boolean flag
        }
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
    def test_get_driver_all_trips(self):
        trip1 = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            service_type='driver_and_car',
            driver_status='waiting',
            status='upcoming',
            estimated_time="10 mins"
        )
        trip2 = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            service_type='driver_only',
            driver_status='completed',
            status='completed',
            estimated_time="30 mins"
        )
        
        url = reverse('get_driver_all_trips')
        payload = {
            "driverid": self.driver_user.custom_id
        }
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        self.assertEqual(len(data['body']), 2)

    def test_request_trip_completion(self):
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            service_type='driver_and_car',
            driver_status='coming',
            status='active',
            estimated_time="10 mins"
        )
        
        url = reverse('request_trip_completion')
        payload = {
            "trip_id": trip.trip_id
        }
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
    def test_confirm_trip_completion(self):
        trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            service_type='driver_and_car',
            driver_status='coming',
            status='active',
            estimated_time="10 mins"
        )
        
        url = reverse('confirm_trip_completion')
        payload = {
            "trip_id": trip.trip_id,
            "userid": self.customer.custom_id
        }
        
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['status'])
        
        trip.refresh_from_db()
        self.assertEqual(trip.status, 'completed')
