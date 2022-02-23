from decimal import Decimal
from django.db.models import F, Sum, Prefetch, Q
from product.models import Item, Bucket, Promocode, BucketItems


def count_order_sum(user):
    items_query = Item.objects.filter(
        item_bucket__owner_id=user.id
    ).annotate(
        total_price=F("price") * F("bucket_items_item__count"),
        count_=F("bucket_items_item__count"),
        bucketitem_id=F("bucket_items_item__id")
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
    bucket_total_price = queryset.first().bucket_total_price
    return bucket_total_price


def count_promocode(self, request, promocode_user):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
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
            bucket_total_price = queryset.first().bucket_total_price
            return bucket_total_price
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
            bucket_total_price = tprice_item_bucket_without_discount * promocode_discount_coefficient + tprice_item_bucket_with_discount
            return bucket_total_price
