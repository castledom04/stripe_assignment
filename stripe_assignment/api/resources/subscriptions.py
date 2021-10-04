from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..exceptions import PaymentsCardError, PaymentsGatewayError
from ..serializers import SubscribeSerializer
from ..services import PaymentsGateway


class SubscriptionsViewSet(viewsets.ViewSet):

    @extend_schema(
        request=SubscribeSerializer,
        responses=SubscribeSerializer,
        description="Super method man!"
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='subscribe')
    def subscribe(self, request):

        serializer = SubscribeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                gateway = PaymentsGateway()
                gateway.create_subscription(request.user, serializer.validated_data)

            except PaymentsCardError as e:
                return Response(
                    {"non_field_errors": [e.message]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except PaymentsGatewayError as e:
                return Response(
                    {"non_field_errors": [e.message]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='status')
    def status(self, request):
        return Response("OK")

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='stripe-webhook')
    def stripe_webhook(self, request):
        print('request', request)
        return Response("OK")
