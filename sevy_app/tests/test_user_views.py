from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from sevy_app.models import UserSearch

User = get_user_model()

class UserViewsTests(APITestCase):
    def setUp(self):
        # Create a user to test with
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            user_type='customer'
        )
        self.userid = self.user.custom_id
        
        self.most_searched_url = reverse('user_most_searched')

    def test_most_searched_places_success(self):
        # Create some search history
        UserSearch.objects.create(user=self.user, search_type='place', search_string='Kigali')
        UserSearch.objects.create(user=self.user, search_type='place', search_string='Kigali')
        UserSearch.objects.create(user=self.user, search_type='place', search_string='Kigali')
        UserSearch.objects.create(user=self.user, search_type='place', search_string='Gisenyi')
        UserSearch.objects.create(user=self.user, search_type='place', search_string='Gisenyi')
        UserSearch.objects.create(user=self.user, search_type='place', search_string='Musanze')
        
        # Ignored because search_type is not 'place'
        UserSearch.objects.create(user=self.user, search_type='coordinates', search_string='-1.0,30.0')

        data = {
            'userid': self.userid
        }
        response = self.client.post(self.most_searched_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertTrue(response.data['status'])
        
        results = response.data['body']['results']
        self.assertEqual(len(results), 3)
        
        # Check ordering
        self.assertEqual(results[0]['locationname'], 'Kigali')
        self.assertEqual(results[0]['search_count'], 3)
        
        self.assertEqual(results[1]['locationname'], 'Gisenyi')
        self.assertEqual(results[1]['search_count'], 2)
        
        self.assertEqual(results[2]['locationname'], 'Musanze')
        self.assertEqual(results[2]['search_count'], 1)

    def test_most_searched_missing_userid(self):
        response = self.client.post(self.most_searched_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
        self.assertFalse(response.data['status'])
        self.assertIn('userid', response.data['message'])

    def test_most_searched_invalid_userid(self):
        data = {
            'userid': 'invalid_id'
        }
        response = self.client.post(self.most_searched_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 404)
        self.assertFalse(response.data['status'])
