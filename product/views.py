from django.db.models import F, Q, Prefetch, Sum, Value, FloatField, DecimalField
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.response import Response
from product.models import Item, Bucket, BucketItems, Promocode, Cashback, Order, UseCashbackAmount
from product.serializers import ListItemSerializer, RetrieveItemSerializer, BucketSerializer, AddBucketSerializer, \
    RetrieveItemBucketSerializer, UpdateBucketItemsSerializer, AddDiscountSerializer, AddItemSerializer, \
    UpdateItemSerializer, UpdatePromocodeSerializer, PromocodeSerializer, AddPromocodeSerializer, \
    UpdateBucketPromocodeTotalPriceSerializer, CashbackSerializer, UpdateCashbackSerializer, CheckoutSerializer, \
    BucketTotalPriceSerialzer, AddCashbackSerializer, CashbackPaymentSerializer
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from decimal import Decimal
from product.utils import count_order_sum


class HasPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        group_user = user.groups.first().name
        if group_user == "Managers":
            return True
        return False


class ListApiItem(ListAPIView):
    serializer_class = ListItemSerializer

    def get_queryset(self):
        queryset = Item.objects.all(
        ).annotate(
            price_include_discount=F("price") * (100 - F("discount_percent")) / 100
        )
        return queryset


class RetrieveApiItem(RetrieveAPIView):
    serializer_class = RetrieveItemSerializer
    queryset = Item.objects.all()


class AddApiItem(CreateAPIView):
    serializer_class = AddItemSerializer
    permission_classes = [HasPermission]


class DeleteApiItem(DestroyAPIView):
    permission_classes = [HasPermission]
    queryset = Item.objects


class UpdateApiItem(RetrieveUpdateAPIView):
    serializer_class = UpdateItemSerializer
    permission_classes = [HasPermission]
    queryset = Item.objects


class BucketApi(ListAPIView):
    serializer_class = BucketSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            items_query = Item.objects.filter(
                item_bucket__owner_id=user.id
            ).annotate(
                total_price_item=F("price") * F("bucket_items_item__count"),
                count=F("bucket_items_item__count"),
                bucketitem_id=F("bucket_items_item__id"),
                price_include_discount=F("price") * (100 - F("discount_percent")) / 100 * F("bucket_items_item__count")
            )
            queryset = Bucket.objects.filter(
                owner_id=user.id
            ).prefetch_related(
                Prefetch("items", items_query)
            ).annotate(
                bucket_total_price=Sum(
                    (F("items__price") * (100 - F("items__discount_percent")) / 100) * \
                    F("bucket_items_bucket__count")),
                amount_accrued_cashback_=F("owner__amount_accrued_cashback")
            )
        else:
            if "bucket_id" in self.request.cookies:
                queryset = Bucket.objects.filter(id=self.request.cookies.get("bucket_id"))
            else:
                queryset = Bucket.objects.none()
        return queryset


class AddBucketApi(CreateAPIView):
    serializer_class = AddBucketSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_id = kwargs["pk"]
        item_count = serializer.validated_data["count"]
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        if item_count != 0:
            if request.user.is_authenticated:
                user = request.user
                bucket_id = user.bucket_set.first().id
            else:
                if "bucket_id" in request.cookies:
                    bucket_id = request.cookies["bucket_id"]
                else:
                    bucket_id = Bucket.objects.create().id
                    response.set_cookie("bucket_id", bucket_id)
            order_query = BucketItems.objects.filter(bucket_id=bucket_id, item_id=item_id)
            if order_query.exists():
                order = order_query.first()
                order.count += item_count
                if order.count <= 0:
                    order.delete()
                    return response
                order.save()
            else:
                BucketItems.objects.create(count=item_count, bucket_id=bucket_id, item_id=item_id)
            return response
        return Response(serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)


class RetrieveApiBucketItem(RetrieveAPIView):
    serializer_class = RetrieveItemBucketSerializer

    def get_queryset(self):
        queryset = BucketItems.objects.all().annotate(
            price_include_discount=F("item__price") * (100 - F("item__discount_percent")) / 100,
            title=F("item__title"),
            description=F("item__description"),
            price=F("item__price"),
            discount_percent=F("item__discount_percent"),
            total_price_item=F("count") * (F("item__price") * (100 - F("item__discount_percent")) / 100)
        )
        return queryset


class DeleteBucketApiItem(DestroyAPIView):
    queryset = BucketItems.objects


class UpdateBucketApiItem(RetrieveUpdateAPIView):
    serializer_class = UpdateBucketItemsSerializer

    def get_queryset(self):
        bucket_id = self.request.COOKIES.get("bucket_id")
        if bucket_id is None:
            if self.request.user.is_authenticated:
                bucket_id = self.request.user.bucket_set.first().id
            else:
                return BucketItems.objects.none()
        return BucketItems.objects.filter(bucket_id=bucket_id, item_id=self.kwargs['pk'])


class AddDiscountApi(UpdateAPIView):
    serializer_class = AddDiscountSerializer
    permission_classes = [HasPermission]
    queryset = Item.objects


class PromocodeApi(ListAPIView):
    serializer_class = PromocodeSerializer
    permission_classes = [HasPermission]
    queryset = Promocode.objects


class AddPromocodeApi(CreateAPIView):
    serializer_class = AddPromocodeSerializer
    permission_classes = [HasPermission]


class UpdatePromocodeApi(UpdateAPIView):
    serializer_class = UpdatePromocodeSerializer
    permission_classes = [HasPermission]
    queryset = Promocode.objects


class DeletePromocodeApi(DestroyAPIView):
    permission_classes = [HasPermission]
    queryset = Promocode.objects


class UpdateBucketApiPromocodeTotalPrice(APIView):
    serializer_class = UpdateBucketPromocodeTotalPriceSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        promocode_user = serializer.validated_data['promocode']
        promocode_query = Promocode.objects.filter(name=promocode_user)
        user = request.user
        bucket_id = user.bucket_set.first().id
        if promocode_query.exists():
            promocode_discount_coefficient = Decimal((100 - Promocode.objects.first().promocode_discount_percent) / 100)
            if Promocode.objects.first().promocode_summ_discount:
                queryset = Bucket.objects.filter(id=bucket_id
                                                 ).annotate(
                    bucket_total_price=Sum(
                        (F("items__price") * (100 - F("items__discount_percent")) / 100) * \
                        F("bucket_items_bucket__count")) * promocode_discount_coefficient
                )
                return Response(BucketTotalPriceSerialzer(queryset.first()).data)
            else:
                tprice_item_bucket_without_discount = 0
                tprice_item_bucket_with_discount = 0
                item_bucket_without_discount = BucketItems.objects.filter(
                    Q(item__in=Item.objects.filter(discount_percent=0))
                )
                item_bucket_with_discount = BucketItems.objects.exclude(
                    Q(item__in=Item.objects.filter(discount_percent=0))
                )
                for item in item_bucket_without_discount:
                    price_item = item.item.price
                    price_item_count = price_item * item.count
                    tprice_item_bucket_without_discount += price_item_count
                for item in item_bucket_with_discount:
                    price_item = item.item.price
                    discount_item = item.item.discount_percent
                    price_item_count_with_discount = price_item * (100 - discount_item) / 100 * item.count
                    tprice_item_bucket_with_discount += price_item_count_with_discount
                bucket_total_price = tprice_item_bucket_without_discount * promocode_discount_coefficient + \
                                     tprice_item_bucket_with_discount
                return Response({"bucket_total_price": bucket_total_price})
        else:
            return Response("Promocode is not valid", status=status.HTTP_406_NOT_ACCEPTABLE)


class CashbackAPI(ListAPIView):
    serializer_class = CashbackSerializer
    permission_classes = [HasPermission]
    queryset = Cashback.objects


class AddCashbackApi(CreateAPIView):
    serializer_class = AddCashbackSerializer
    permission_classes = [HasPermission]


class UpdateCashbackAPI(RetrieveUpdateAPIView):
    serializer_class = UpdateCashbackSerializer
    permission_classes = [HasPermission]
    queryset = Cashback.objects


class CheckoutAPI(CreateAPIView):
    serializer_class = CheckoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        order_sum = count_order_sum(user)
        Order.objects.create(account=user, order_sum=order_sum)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CashbackPaymentAPI(APIView):
    serializer_class = CashbackPaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        cashback_payment = serializer.validated_data['cashback_payment']
        user = self.request.user
        user_cashback = user.amount_accrued_cashback
        min_amount_use_cashback = UseCashbackAmount.objects.first().min_amount_use_cashback
        if user_cashback >= min_amount_use_cashback:
            bucket_total_price = count_order_sum(user)
            bucket_total_price -= cashback_payment
            user_cashback -= cashback_payment
            user.amount_accrued_cashback = user_cashback
            user.save()
            return Response({"bucket_total_price": bucket_total_price, "amount_accrued_cashback": user_cashback})
        return Response(
            "The amount of accrued cashback is less than the minimum usage threshold", status=status.HTTP_406_NOT_ACCEPTABLE
        )

