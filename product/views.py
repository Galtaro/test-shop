from django.db.models import F, Q, Prefetch, Sum, Value
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.response import Response
from product.models import Item, Bucket, BucketItems, Promocode
from product.serializers import ListItemSerializer, RetrieveItemSerializer, BucketSerializer, AddBucketSerializer, \
    RetrieveItemBucketSerializer, UpdateBucketItemSerializer, AddDiscountSerializer, AddItemSerializer, \
    UpdateItemSerializer, UpdatePromocodeSerializer, PromocodeSerializer, AddPromocodeSerializer, \
    UpdateBucketPromocodeTotalPriceSerializer
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from decimal import Decimal


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
                total_price=F("price") * F("bucket_items_item__count"),
                count_=F("bucket_items_item__count")
            )
            queryset = Bucket.objects.filter(
                owner_id=user.id
            ).prefetch_related(
                Prefetch("items", items_query)
            ).annotate(
                bucket_total_price=Sum(
                    (F("items__price") * (100 - F("items__discount_percent")) / 100) * \
                    F("bucket_items_bucket__count")
                )
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
        queryset = Item.objects.all().annotate(
            price_include_discount=F("price") * (100 - F("discount_percent")) / 100,
        )
        return queryset


class DeleteBucketApiItem(DestroyAPIView):
    queryset = BucketItems.objects


class UpdateBucketApiItem(RetrieveUpdateAPIView):
    serializer_class = UpdateBucketItemSerializer
    queryset = Item.objects.annotate(
        count_=F("bucket_items_item__count")
    )


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
        promocode = serializer.validated_data['promocode']
        promocode_db = Promocode.objects.first().name
        user = request.user
        bucket_id = user.bucket_set.first().id  # TODO
        if promocode == promocode_db:
            promocode_discount_coefficient = Decimal((100 - Promocode.objects.first().promocode_discount_percent) / 100)
            if Promocode.objects.first().promocode_summ_discount:
                queryset = Bucket.objects.filter(id=bucket_id
                                                 ).annotate(
                    bucket_total_price=Sum(
                        (F("items__price") * (100 - F("items__discount_percent")) / 100) * \
                        F("bucket_items_bucket__count")) * promocode_discount_coefficient
                )
                return Response()
            else:
                tprice_item_bucket_without_discount = 0
                tprice_item_bucket_with_discount = 0
                item_bucket_without_discount = BucketItems.objects.filter(
                    Q(item__in=Item.objects.filter(discount_percent=0))
                )
                item_bucket_with_discount = BucketItems.objects.filter(
                    ~Q(item__in=Item.objects.filter(discount_percent=0))
                )
                for item in item_bucket_without_discount:
                    price_item = item.item.price
                    tprice_item_bucket_without_discount += price_item
                for item in item_bucket_with_discount:
                    price_item = item.item.price
                    discount_item = item.item.discount
                    price_item_with_discount = price_item * (100 - discount_item / 100)
                    tprice_item_bucket_with_discount += price_item_with_discount
                queryset = Bucket.objects.filter(id=bucket_id
                                                 ).annotate(
                    bucket_total_price=Value(tprice_item_bucket_without_discount * promocode_discount_coefficient + \
                                             tprice_item_bucket_with_discount)
                )
                return Response()
        else:
            return Response()

