from django.db.models import F, Case, When, IntegerField, DecimalField

from product.models import Item


def create_queryset_item():
    """Create queryset items with additional field - price_include_discount"""

    queryset_item = Item.objects.all(
    ).annotate(
        discount_percent=Case(
            When(promotional_offer_item__discount_percent=None,
                 then=0),
            default=F("promotional_offer_item__discount_percent"),
            output_field=IntegerField()),
        price_include_discount=Case(
            When(promotional_offer_item__discount_percent=None,
                 then=F("price")),
            default=F("price") * (100 - F("promotional_offer_item__discount_percent")) / 100,
            output_field=DecimalField())
        )
    return queryset_item
