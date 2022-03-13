from decimal import Decimal
from product.models import Order, Cashback


def count_amount_of_accrued_cashback(user, order):
    """Count amount of accrued cashback after order payment """

    order_sum = Order.objects.get(id=order.id).order_sum
    queryset_cashback = Cashback.objects.order_by("-min_order_amount")
    for elem_queryset in queryset_cashback:
        if elem_queryset.min_order_amount <= order_sum:
            cashback_percent = elem_queryset.cashback_percent
            order_cashback = order_sum * Decimal(cashback_percent/100)
            user.amount_accrued_cashback += order_cashback
            user.save()
            break
