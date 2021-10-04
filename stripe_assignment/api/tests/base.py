from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class BaseAPITestCase(APITestCase):

    def post(self, url, data, user=None, **extra):
        self._authenticate_user(user)
        return self.client.post(path=url, data=data, format='json', **extra)

    def get(self, url, user=None, **extra):
        self._authenticate_user(user)
        return self.client.get(path=url, format='json', **extra)

    def put(self, url, data, user=None, **extra):
        self._authenticate_user(user)
        return self.client.put(path=url, data=data, format='json', **extra)

    def patch(self, url, data, user=None, **extra):
        self._authenticate_user(user)
        return self.client.patch(path=url, data=data, format='json', **extra)

    def delete(self, url, user=None, **extra):
        self._authenticate_user(user)
        return self.client.delete(path=url, **extra)

    def _authenticate_user(self, user):
        if user is not None:
            refresh = RefreshToken.for_user(user)
            self.client.credentials(HTTP_AUTHORIZATION=f'JWT {str(refresh.access_token)}')
