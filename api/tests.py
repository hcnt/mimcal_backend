from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from main.models import User, Schedule, EventType, Event, Comment
from rest_framework.test import force_authenticate
from rest_framework.authtoken.models import Token


def create_test_account(client, username='test'):
    url = '/api/v1/auth/register/'
    data = {'username': username, 'password': '123', 'password_confirm': '123'}
    response = client.post(url, data, format='json')
    return response


def login_test_account(client, username='test'):
    url = '/api/v1/auth/login/'
    data = {'login': username, 'password': '123'}
    response = client.post(url, data, format='json')
    client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
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


class ScenarioTests(APITestCase):
    def setUp(self):
        self.event_type_test = EventType.objects.create(name='egzamin')

        self.test_event_data = {'title': 'jakiś-egzamin',
                       'desc': '',
                       'start_date': '2021-02-02T10:00',
                       'end_date': '2021-02-02T12:00',
                       'type': self.event_type_test.id,
                       'schedule': '1'}

    def test_create_schedule(self):
        create_test_account(self.client)
        login_test_account(self.client)
        url = '/api/v1/schedules/'

        data = {'name': 'test_schedule', 'default_permission_level': '1'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(Schedule.objects.get().name, 'test_schedule')

    def assertScheduleReadAccess(self, has_access):
        url = '/api/v1/schedules/1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200 if has_access else 404)

        url = '/api/v1/schedules/1/events/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200 if has_access else 404)

    def create_schedule_and_event(self,default_level=1):
        url = '/api/v1/schedules/'
        data = {'name': 'mimuw', 'default_permission_level': default_level}

        # Create schedule
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.get().name, 'mimuw')

        url = '/api/v1/events/'
        data = self.test_event_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return Schedule.objects.get(name='mimuw'), Event.objects.get(title='jakiś-egzamin')


    def test_1(self):
        # Normal case with one logged in user

        create_test_account(self.client)
        login_test_account(self.client)
        url = '/api/v1/schedules/'
        data = {'name': 'mimuw', 'default_permission_level': '1'}

        # Create schedule
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(Schedule.objects.get().name, 'mimuw')

        # Get schedule
        url = '/api/v1/schedules/1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'mimuw')

        # Get non existent schedule
        url = '/api/v1/schedules/2/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Add event to schedule
        url = '/api/v1/events/'
        data = self.test_event_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(Schedule.objects.get().event_set.count(), 1)
        self.assertEqual('test' in map(lambda x: x.username, Event.objects.get().users_marks.all()), False)

        # Check event
        url = '/api/v1/events/1/check/'
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if test user is in users marks
        self.assertEqual('test' in map(lambda x: x.username, Event.objects.get().users_marks.all()), True)

        # Uncheck event
        url = '/api/v1/events/1/uncheck/'
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if test user is in users marks
        self.assertEqual('test' in map(lambda x: x.username, Event.objects.get().users_marks.all()), False)

        # check for access to comments
        url = '/api/v1/events/1/comments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = '/api/v1/comments/'
        data = {'content': 'czesc', 'event': '1', 'author_id': '1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.get()
        self.assertEqual(comment.likes_count, 0)

        url = '/api/v1/comments/1/like/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 200)

        comment = Comment.objects.get()
        self.assertEqual(comment.likes_count, 1)

        url = '/api/v1/comments/1/unlike/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 200)

        comment = Comment.objects.get()
        self.assertEqual(comment.likes_count, 0)

    def test_anon(self):
        # anonymous user shoudn't have access to read with permission level 0
        create_test_account(self.client)
        schedule = Schedule.objects.create(name='mimuw', default_permission_level=0,
                                           owner=User.objects.get(username='test'))
        data = self.test_event_data
        data['schedule'] = schedule
        data['type'] = self.event_type_test
        Event.objects.create(**data)
        url = '/api/v1/schedules/1/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = '/api/v1/schedules/1/events/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        schedule.default_permission_level = 1
        schedule.save()

        # now he should have access
        self.assertScheduleReadAccess(True)

    def test_perm(self):
        create_test_account(self.client, username='test')
        create_test_account(self.client, username='test2')


        login_test_account(self.client, username='test')

        schedule, event = self.create_schedule_and_event(0)


        login_test_account(self.client, username='test2')

        self.assertScheduleReadAccess(False)
        # make defalut permission less strict
        schedule.default_permission_level = 1
        schedule.save()

        self.assertScheduleReadAccess(True)


    def test_perm_2(self):
        create_test_account(self.client, username='test')
        create_test_account(self.client, username='test2')

        login_test_account(self.client, username='test')

        self.create_schedule_and_event(0)

        login_test_account(self.client, username='test2')

        # check access
        self.assertScheduleReadAccess(False)

        # add permission to test2
        login_test_account(self.client, username='test')
        url = '/api/v1/schedules/1/change_user_perm/'
        response = self.client.post(url, **{'QUERY_STRING': 'username=test2&level=1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check access again
        login_test_account(self.client, username='test2')
        self.assertScheduleReadAccess(True)

    def test_webcal(self):
        create_test_account(self.client)
        schedule = Schedule.objects.create(name='mimuw', default_permission_level=0,
                                           owner=User.objects.get(username='test'))
        data = {'title': 'jakiś egzamin',
                'desc': '',
                'start_date': '2021-02-02T10:00',
                'end_date': '2021-02-02T12:00',
                'type': EventType.objects.get(id=1),
                'schedule': schedule}
        Event.objects.create(**data)

        url = '/api/v1/schedules/1/to_webcal/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
