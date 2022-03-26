from rest_framework import status

from django.db.models import F, Case, When, IntegerField, DecimalField

from product.models import BucketItems


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
            discount_percent=Case(
                When(promotional_offer_item__discount_percent=None,
                     then=0),
                default=F("promotional_offer_item__discount_percent"),
                output_field=IntegerField()),
            total_price_item=Case(
                When(promotional_offer_item__discount_percent=None,
                     then=F("count") * F("item__price")),
                default=F("count") * (F("item__price") * (100 - F("promotional_offer_item__discount_percent")) / 100),
                output_field=DecimalField())
        )
    return queryset
