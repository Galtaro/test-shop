from rest_framework import status
from product.models import BucketItems
from django.db.models import F


def create_bucket_item(item_count, item_id, bucket_id):
    """Create bucket item or if bucket item exists update field count, return status code"""

    order_query = BucketItems.objects.filter(bucket_id=bucket_id, item_id=item_id)
    if order_query.exists():
        order = order_query.first()
        order.count += item_count
        order.save()
        return status.HTTP_200_OK
    else:
        BucketItems.objects.create(count=item_count, bucket_id=bucket_id, item_id=item_id)
        return status.HTTP_201_CREATED


def queryset_bucket_items():
    """Returns the queryset bucket items with additional fields - price_include_discount, title, description,
     price, discount_percent, total_price_item"""

    queryset = BucketItems.objects.all().annotate(
            price_include_discount=F("item__price") * (100 - F("item__discount_percent")) / 100,
            title=F("item__title"),
            description=F("item__description"),
            price=F("item__price"),
            discount_percent=F("item__discount_percent"),
            total_price_item=F("count") * (F("item__price") * (100 - F("item__discount_percent")) / 100)
        )
    return queryset
