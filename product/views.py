from django.db.models import F, Prefetch
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.response import Response
from product.models import Item, Bucket, BucketItems
from product.serializers import ListItemSerializer, RetrieveItemSerializer, BucketSerializer, AddBucketSerializer, \
    RetrieveItemBucketSerializer, UpdateBucketItemSerializer


class ListApiItem(ListAPIView):
    serializer_class = ListItemSerializer
    queryset = Item.objects.all()


class RetrieveApiItem(RetrieveAPIView):
    serializer_class = RetrieveItemSerializer
    queryset = Item.objects.all()


class BucketApi(ListAPIView):
    serializer_class = BucketSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            items_query = Item.objects.filter(
                item_bucket__owner_id=user.id
            ).annotate(
                total_price=F("price") * F("bucket_items_item__count")
            ).annotate(
                count=F("bucket_items_item__count")
            )
            queryset = Bucket.objects.filter(
                owner_id=user.id
            ).prefetch_related(
                Prefetch("items", items_query)
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
        item_count = serializer.validated_data["count"]
        item_id = kwargs["pk"]
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
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
            order.save()
        else:
            BucketItems.objects.create(count=item_count, bucket_id=bucket_id, item_id=item_id)
        return response


class RetrieveApiBucketItem(RetrieveAPIView):
    serializer_class = RetrieveItemBucketSerializer
    queryset = Item.objects.all()


class DeleteBucketApiItem(DestroyAPIView):
    queryset = Item.objects


class UpdateBucketApiItem(UpdateAPIView):
    serializer_class = UpdateBucketItemSerializer
    queryset = Item.objects.annotate(
                count=F("bucket_items_item__count")
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        item_id = kwargs["pk"]
        item_new_count = serializer.validated_data["count"]
        bucket_items_query = BucketItems.objects.filter(item_id=item_id)
        if bucket_items_query.exists():
            bucket_item = bucket_items_query.first()
            bucket_item.count = item_new_count
            bucket_item.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.data, status=status.HTTP_406_NOT_ACCEPTABLE)
