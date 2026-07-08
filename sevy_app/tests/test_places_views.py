from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from sevy_app.models import Location, UserSearch

User = get_user_model()

class PlacesViewsTests(APITestCase):
    def setUp(self):
        # Create a user to test with
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            user_type='customer'
        )
        self.userid = self.user.custom_id

        # Create some locations
        Location.objects.create(user=self.user, locationname="Kigali City Center", latitude=-1.944, longitude=30.061)
        Location.objects.create(user=self.user, locationname="Kigali Airport", latitude=-1.968, longitude=30.133)

        self.text_search_url = reverse('place-search-text')
        self.coord_search_url = reverse('place-search-coordinates')
        self.save_search_url = reverse('place-search-save')

    def test_text_search_success(self):
        data = {
            'userid': self.userid,
            'search_text': 'Kigali'
        }
        response = self.client.post(self.text_search_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['message'], 'Places retrieved successfully.')
        self.assertEqual(len(response.data['body']['results']), 2)

        # Verify search was logged
        search_log = UserSearch.objects.filter(user=self.user, search_type='place').first()
        self.assertIsNotNone(search_log)
        self.assertEqual(search_log.search_string, 'Kigali')

    def test_text_search_missing_userid(self):
        data = {'search_text': 'Kigali'}
        response = self.client.post(self.text_search_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertFalse(response.data['status'])

    def test_coord_search_success(self):
        data = {
            'userid': self.userid,
            'lat': -1.940,
            'lng': 30.060
        }
        response = self.client.post(self.coord_search_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        
        results = response.data['body']['results']
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['locationname'], 'Kigali City Center') # Closer to coordinates

        # Verify search was logged
        search_log = UserSearch.objects.filter(user=self.user, search_type='coordinates').first()
        self.assertIsNotNone(search_log)
        self.assertEqual(search_log.search_string, '-1.94,30.06')

    def test_coord_search_invalid_data(self):
        data = {'userid': self.userid, 'lat': 'invalid', 'lng': 'invalid'}
        response = self.client.post(self.coord_search_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['status'])
        self.assertIn('Invalid coordinates format.', response.data['message'])

    def test_save_place_selection_success(self):
        data = {
            'userid': self.userid,
            'placeid': 'Kigali City Center'
        }
        response = self.client.post(self.save_search_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        
        # Verify search was logged
        search_log = UserSearch.objects.filter(user=self.user, search_type='place', search_string='Selected Place: Kigali City Center').first()
        self.assertIsNotNone(search_log)

    def test_save_place_selection_invalid_place(self):
        data = {
            'userid': self.userid,
            'placeid': 'Fake Place'
        }
        response = self.client.post(self.save_search_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['status'])
