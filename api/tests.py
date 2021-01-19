from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from main.models import User, Schedule
from rest_framework.test import force_authenticate
from rest_framework.authtoken.models import Token


def create_test_account(client):
    url = '/api/v1/auth/register/'
    data = {'username': 'test', 'password': '123', 'password_confirm': '123'}
    response = client.post(url, data, format='json')
    return response


def login_test_account(client):
    url = '/api/v1/auth/login/'
    data = {'login': 'test', 'password': '123'}
    response = client.post(url, data, format='json')
    return response


class UserTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = '/api/v1/auth/register/'
        data = {'username': 'test', 'password': '123', 'password_confirm': '123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test')


class ScheduleTests(APITestCase):
    def test_create_schedule(self):
        """
        Ensure we can create a new account object.
        """
        create_test_account(self.client)
        response = login_test_account(self.client)
        url = '/api/v1/schedules/'
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

        data = {'name': 'test_schedule', 'default_permission_level': '1'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(Schedule.objects.get().name, 'test_schedule')
