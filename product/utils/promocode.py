from decimal import Decimal
from django.db.models import Sum, F, Q, Case, When, DecimalField

from product.models import Promocode, Bucket, Item, BucketItems, PromotionalOffer


def count_bucket_total_price_after_use_promocode(promocode_user, bucket_id):
    """Count bucket total price after use promocode"""

    promocode_query = Promocode.objects.filter(name=promocode_user)
    promocode_discount_coefficient = count_promocode_discount_coefficient()
    if promocode_query.first().promocode_summ_discount:
        queryset = create_queryset_bucket_ann_bucket_total_price_with_promocode(bucket_id)
        bucket_total_price = queryset.first().bucket_total_price
        return bucket_total_price
    else:
        tprice_item_bucket_without_discount = 0
        tprice_item_bucket_with_discount = 0
        item_bucket_without_discount = count_item_bucket_without_discount()
        item_bucket_with_discount = count_item_bucket_with_discount()
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


def count_promocode_discount_coefficient():
    """Count discount coefficient of promocode"""

    promocode_discount_coefficient = Decimal((100 - Promocode.objects.first().promocode_discount_percent) / 100)
    return promocode_discount_coefficient


def create_queryset_bucket_ann_bucket_total_price_with_promocode(bucket_id):
    """Create queryset bucket with annotations field bucket total price with discount promocode"""

    queryset = Bucket.objects.filter(id=bucket_id
                                     ).annotate(
        bucket_total_price=Sum(
            Case(
                When(promotional_offer_item__discount_percent=None,
                     then=F("items__price") * F("bucket_items_bucket__count") * count_promocode_discount_coefficient()),
                default=(F("items__price") * (100 - F("items__discount_percent")) / 100)
                * F("bucket_items_bucket__count") * count_promocode_discount_coefficient(),
                output_field=DecimalField())
        )
    )
    return queryset


def count_item_bucket_without_discount():
    """Count price bucket item without discount"""

    item_bucket_without_discount = BucketItems.objects.filter(
        Q(item__in=PromotionalOffer.objects.all())
    )
    return item_bucket_without_discount


def count_item_bucket_with_discount():
    """Count price bucket item with discount"""

    item_bucket_with_discount = BucketItems.objects.exclude(
        Q(item__in=PromotionalOffer.objects.all())
    )
    return item_bucket_with_discount


def set_cookie_promocode(response, promocode_user):
    """Set promocode into the cookie"""

    response.set_cookie("promocode", promocode_user, 600)
    return response
