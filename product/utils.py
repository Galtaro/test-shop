from django.db.models import F, Sum, Prefetch

from product.models import Item, Bucket


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
