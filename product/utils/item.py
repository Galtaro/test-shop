from django.db.models import F

from product.models import Item


def create_queryset_item():
    """Create queryset items with additional field - price_include_discount"""

    queryset_item = Item.objects.all(
            ).annotate(
        price_include_discount=F("price") * (100 - F("discount_percent")) / 100
    )
    return queryset_item
