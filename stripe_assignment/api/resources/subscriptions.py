from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from ..exceptions import (PaymentsAlreadySubscribedError, PaymentsCardError,
                          PaymentsGatewayError)
from ..serializers import StatusSerializer, SubscribeSerializer
from ..services import PaymentsGateway, PaymentsWebhook


class SubscriptionsViewSet(viewsets.ViewSet):

    @extend_schema(
        request=SubscribeSerializer,
        responses=SubscribeSerializer,
        description="""
            Endpoint to subscribe to stripe when passing the valid data.
            If there is an existing customer, payment method or subscription for the
            requester user, it will be not created again.
        """
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
            except PaymentsAlreadySubscribedError as e:
                return Response(
                    {"non_field_errors": [e.message]},
                    status=status.HTTP_409_CONFLICT
                )

        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        request=StatusSerializer,
        responses={
            200: StatusSerializer,
            404: {}
        },
        description="""
            Endpoint to return the current subscription for the requester user, if any.
            If there is not a created subscription the response status will be 404.
        """
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated], url_path='status')
    def status(self, request):
        subscription = request.user.get_subscription()
        if subscription:
            serializer = StatusSerializer(instance=subscription)
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)


class StripeWebookView(APIView):

    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        description="""
            Endpoint to handle stripe webhook events. Always returns a response status 200.
        """
    )
    def post(self, request, format=None):
        webhook = PaymentsWebhook()
        webhook.handle_event(request)
        return Response("OK")
