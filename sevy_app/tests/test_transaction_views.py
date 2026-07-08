from django.test import TestCase, Client
from django.urls import reverse
from sevy_app.models import CustomUser, Driver, Trip, Transaction
import json

class TransactionAPITests(TestCase):
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
        
        self.trip = Trip.objects.create(
            userid=self.customer,
            driverid=self.driver,
            estimated_time="15 mins",
            total_price=5000.00,
            status="completed"
        )

        self.create_url = reverse('create_transaction')

    def test_create_transaction_success(self):
        payload = {
            "userid": self.customer.custom_id,
            "amount": 5000.00,
            "payment_method": "momo",
            "transaction_type": "trip",
            "reference_number": "MOMO123456789",
            "trip_id": self.trip.trip_id,
            "is_success": True
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        self.assertTrue(response_data['status'])
        
        # Verify transaction was created
        tx_id = response_data['body']['transaction_id']
        tx = Transaction.objects.get(transaction_id=tx_id)
        
        self.assertEqual(tx.user, self.customer)
        self.assertEqual(tx.amount, 5000.00)
        self.assertEqual(tx.reference_number, "MOMO123456789")
        
        # Verify trip was updated
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.payment_status, 'paid')
        self.assertEqual(self.trip.transaction, tx)

    def test_create_transaction_duplicate(self):
        # Create an existing transaction
        Transaction.objects.create(
            user=self.customer,
            amount=5000.00,
            payment_method="momo",
            transaction_type="trip",
            reference_number="DUPLICATE123",
            status="completed"
        )
        
        payload = {
            "userid": self.customer.custom_id,
            "amount": 5000.00,
            "payment_method": "momo",
            "transaction_type": "trip",
            "reference_number": "DUPLICATE123",
            "trip_id": self.trip.trip_id,
            "is_success": True
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.json()['status'])

    def test_create_transaction_invalid_trip(self):
        payload = {
            "userid": self.customer.custom_id,
            "amount": 5000.00,
            "payment_method": "momo",
            "transaction_type": "trip",
            "reference_number": "MOMO98765",
            "trip_id": "invalid_trip_id",
            "is_success": True
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['status'])

    def test_create_transaction_pending(self):
        payload = {
            "userid": self.customer.custom_id,
            "amount": 5000.00,
            "payment_method": "momo",
            "transaction_type": "trip",
            "reference_number": "PENDING123",
            "trip_id": self.trip.trip_id,
            "is_pending": True
        }
        
        response = self.client.post(self.create_url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
        response_data = response.json()
        tx_id = response_data['body']['transaction_id']
        tx = Transaction.objects.get(transaction_id=tx_id)
        
        self.assertEqual(tx.status, 'pending')
        
        # Verify trip was NOT updated to paid
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.payment_status, 'unpaid')
