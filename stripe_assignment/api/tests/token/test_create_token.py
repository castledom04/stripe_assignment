import jwt
from django.conf import settings
from django.urls import reverse
from expects import be_true, equal, expect, raise_error
from rest_framework import status

from ...models import Account, User
from ..base import BaseAPITestCase


class CreateTokenTestCase(BaseAPITestCase):

    def setUp(self):
        self.url = reverse('token_create')

    def test_it_returns_not_allowed_for_get_method(self):
        response = self.get(url=self.url, user=None, data={})

        expect(response.status_code).to(equal(status.HTTP_405_METHOD_NOT_ALLOWED))

    def test_it_returns_unauthorized_with_wrong_credentials(self):
        data = {
            'username': 'non existing user',
            'password': 'non existing password'
        }

        response = self.post(url=self.url, user=None, data=data)

        expect(response.status_code).to(equal(status.HTTP_401_UNAUTHORIZED))

    def test_it_returns_valid_token_with_existing_credentials(self):
        account = Account.objects.create(name="User account")
        User.objects.create_user(
            username='goku',
            password='goku1234',
            account=account
        )
        data = {
            'username': 'goku',
            'password': 'goku1234'
        }

        response = self.post(url=self.url, user=None, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect('access' in response.json()).to(be_true)
        expect('refresh' in response.json()).to(be_true)
        expect(
            jwt.decode(response.json()['refresh'], settings.JWT_VERIFYING_KEY, algorithms=['RS256'])
        ).not_to(raise_error(jwt.exceptions.InvalidSignatureError))

    def test_it_returns_valid_token_data(self):
        account = Account.objects.create(name="User account")
        user = User.objects.create_user(
            username='goku',
            password='goku1234',
            account=account
        )
        data = {
            'username': 'goku',
            'password': 'goku1234'
        }

        response = self.post(url=self.url, user=None, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        token = jwt.decode(response.json()['access'], settings.JWT_VERIFYING_KEY, algorithms=['RS256'])
        expect(token['id']).to(equal(f'{user.id}'))
        expect(token['app_name']).to(equal("Stripe Assignment"))
