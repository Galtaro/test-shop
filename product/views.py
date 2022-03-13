from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django_celery_beat.models import PeriodicTask, ClockedSchedule
from json import dumps
from datetime import timedelta

from product.models import Item, BucketItems, Promocode, Cashback, EmailDeliveryNotification
from product.serializers import ListItemSerializer, RetrieveItemSerializer, ListBucketSerializer, \
    CreateBucketItemSerializer, RetrieveItemBucketSerializer, UpdateBucketItemsSerializer, \
    UpdateDiscountSerializer, CreateItemSerializer, UpdateItemSerializer, UpdatePromocodeSerializer, \
    ListPromocodeSerializer, UpdateBucketPromocodeTotalPriceSerializer, ListCashbackSerializer, \
    UpdateCashbackSerializer, CreateCheckoutSerializer, CashbackPaymentSerializer
from product.utils.bucket import queryset_bucket_specific_user, create_order
from product.utils.bucket_item import create_bucket_item, queryset_bucket_items
from product.utils.cashback import count_bucket_total_price_with_cashback
from product.utils.create_tasks import create_task_send_notification
from product.utils.item import create_queryset_item
from product.utils.promocode import count_bucket_total_price_after_use_promocode, set_cookie_promocode

class HasPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        group_user = user.groups.first().name
        return group_user == "Managers"


class ListApiItem(ListAPIView):
    serializer_class = ListItemSerializer

    def get_queryset(self):
        queryset_item = create_queryset_item()
        return queryset_item


class RetrieveApiItem(RetrieveAPIView):
    serializer_class = RetrieveItemSerializer
    queryset = Item.objects.all()


class CreateApiItem(CreateAPIView):
    serializer_class = CreateItemSerializer
    permission_classes = [IsAuthenticated, HasPermission]


class UpdateDestroyApiItem(RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateItemSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Item.objects


class ListApiBucket(ListAPIView):
    serializer_class = ListBucketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        queryset_bucket = queryset_bucket_specific_user(user_id=user_id)
        return queryset_bucket


class CreateApiBucketItem(CreateAPIView):

    serializer_class = CreateBucketItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_count = serializer.validated_data["count"]
        item_id = kwargs["pk"]
        user = request.user
        bucket_id = user.bucket_set.first().id
        status_code = create_bucket_item(
            item_count=item_count,
            item_id=item_id,
            bucket_id=bucket_id
        )
        return Response(serializer.data, status=status_code)


class RetrieveApiBucketItem(RetrieveAPIView):

    serializer_class = RetrieveItemBucketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = queryset_bucket_items()
        return queryset


class UpdateDestroyApiBucketItem(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateBucketItemsSerializer

    def get_queryset(self):
        bucket_id = self.request.user.bucket_set.first().id
        queryset = BucketItems.objects.filter(bucket_id=bucket_id, id=self.kwargs['pk'])
        return queryset


class UpdateApiDiscount(UpdateAPIView):
    serializer_class = UpdateDiscountSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Item.objects


class ListCreateApiPromocode(ListCreateAPIView):
    serializer_class = ListPromocodeSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Promocode.objects


class UpdateDestroyApiPromocode(UpdateDestroyApiItem):
    serializer_class = UpdatePromocodeSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Promocode.objects


class UpdateApiBucketPromocodeTotalPrice(APIView):
    serializer_class = UpdateBucketPromocodeTotalPriceSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        promocode_user = serializer.validated_data['promocode']
        user = request.user
        bucket_id = user.bucket_set.first().id
        bucket_total_price = count_bucket_total_price_after_use_promocode(
            promocode_user=promocode_user,
            bucket_id=bucket_id
        )
        response = Response({"bucket_total_price": bucket_total_price})
        set_cookie_promocode(response, promocode_user)
        return response


class ListCreateApiCashback(ListCreateAPIView):
    serializer_class = ListCashbackSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Cashback.objects


class UpdateApiCashback(RetrieveUpdateAPIView):
    serializer_class = UpdateCashbackSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    queryset = Cashback.objects


class CreateApiCheckout(CreateAPIView):
    serializer_class = CreateCheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_date_time = serializer.validated_data['delivery_date_time']
        email_delivery_notification = serializer.validated_data['email_delivery_notification']
        email_delivery_notification = EmailDeliveryNotification.objects.get(
            title=email_delivery_notification)
        user = self.request.user
        email = user.email
        bucket = user.bucket_set.first().id
        order = create_order(
            user=user,
            bucket=bucket,
            delivery_date_time=delivery_date_time,
            email_delivery_notification=email_delivery_notification
        )
        create_task_send_notification(
            email_delivery_notification=email_delivery_notification,
            delivery_date_time=delivery_date_time,
            order=order,
            email=email
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApiCashbackPayment(APIView):
    serializer_class = CashbackPaymentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        cashback_payment = serializer.validated_data['cashback_payment']
        user = self.request.user
        promocode_user = request.COOKIES.get("promocode")
        bucket_total_price, user_cashback = count_bucket_total_price_with_cashback(
            user=user,
            promocode_user=promocode_user,
            cashback_payment=cashback_payment
        )
        return Response(
            {"bucket_total_price": bucket_total_price,
            "amount_accrued_cashback": user_cashback}
        )

