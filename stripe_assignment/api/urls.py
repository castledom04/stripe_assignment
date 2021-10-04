from django.conf.urls import include, url
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from .resources import ObtainTokenPairView, SubscriptionsViewSet, StripeWebookView

router = routers.DefaultRouter()
router.register(r'subscriptions', SubscriptionsViewSet, basename='subscriptions')

urlpatterns = [
    path('token/obtain/', ObtainTokenPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('stripe-webhook/', StripeWebookView.as_view(), name='stripe-webhook'),
    url(r'', include(router.urls)),
]

urlpatterns += [
    url(r'schema/', SpectacularAPIView.as_view(), name="schema"),
    url(
        r'docs/',
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),
]
