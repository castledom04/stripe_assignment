from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers import MyTokenObtainPairSerializer


class ObtainTokenPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer
