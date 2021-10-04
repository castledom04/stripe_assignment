from django.urls import reverse
from expects import equal, expect
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from ...models import Account, User
from ..base import BaseAPITestCase


class RefreshTokenTestCase(BaseAPITestCase):

    def setUp(self):
        self.url = reverse('token_refresh')

    def test_it_returns_not_allowed_for_get_method(self):
        response = self.get(url=self.url, user=None, data={})

        expect(response.status_code).to(equal(status.HTTP_405_METHOD_NOT_ALLOWED))

    def test_it_returns_unauthorized_with_wrong_token(self):
        data = {
            'refresh': 'ajs8dj9as8dn9a8shdna9s8dh9'
        }

        response = self.post(url=self.url, user=None, data=data)

        expect(response.status_code).to(equal(status.HTTP_401_UNAUTHORIZED))

    def test_it_returns_the_new_access_token(self):
        account = Account.objects.create(name="User account")
        user = User.objects.create_user(
            username='goku',
            password='goku1234',
            account=account
        )
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh)
        }

        response = self.post(url=self.url, user=None, data=data)

        expect(response.status_code).to(equal(status.HTTP_200_OK))
        expect(response.json()['access']).not_to(equal(str(refresh.access_token)))
