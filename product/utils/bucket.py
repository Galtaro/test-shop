from django.db.models import F, Sum, Prefetch

from product.models import Item, Bucket, BucketItems, Order


def queryset_items_in_bucket_specific_user(user_id):
    """Returns the queryset items in a specified user's bucket with additional fields - total_price_item,
    count, bucketitem_id, price_include_discount"""

    items_query = Item.objects.filter(
        item_bucket__owner_id=user_id
    ).annotate(
        total_price_item=F("price") * F("bucket_items_item__count"),
        count=F("bucket_items_item__count"),
        bucketitem_id=F("bucket_items_item__id"),
        price_include_discount=F("price") * (100 - F("discount_percent")) / 100 * F("bucket_items_item__count")
    )
    return items_query


def queryset_bucket_specific_user(user_id):
    """Returns the queryset of a specific user's bucket with additional fields - bucket_total_price,
    amount_accrued_cashback """

    queryset_bucket = Bucket.objects.filter(
        owner_id=user_id
    ).prefetch_related(
        Prefetch("items", queryset_items_in_bucket_specific_user(user_id))
    ).annotate(
        bucket_total_price=Sum(
            (F("items__price") * (100 - F("items__discount_percent")) / 100) * \
            F("bucket_items_bucket__count")),
        amount_accrued_cashback_=F("owner__amount_accrued_cashback")
    )
    return queryset_bucket


def create_order(user, bucket, delivery_date_time, email_delivery_notification):
    """ Count bucket total price after use checkout, create order, empty the bucket"""

    queryset = queryset_bucket_specific_user(user.id)
    order_sum = queryset.first().bucket_total_price
    order = Order.objects.create(
        account=user,
        order_sum=order_sum,
        delivery_date_time=delivery_date_time,
        email_delivery_notification=email_delivery_notification)
    BucketItems.objects.filter(bucket=bucket).delete()
    return order
