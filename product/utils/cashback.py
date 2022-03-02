from product.utils.bucket import queryset_bucket_specific_user
from product.utils.promocode import count_bucket_total_price_after_use_promocode


def count_bucket_total_price_with_cashback(user, promocode_user, cashback_payment):
    """Count bucket total price after use cashback and count rest of user amount accrued cashback"""

    user_cashback = user.amount_accrued_cashback
    if promocode_user:
        bucket_id = user.bucket_set.first().id
        bucket_total_price = count_bucket_total_price_after_use_promocode(promocode_user, bucket_id)
    else:
        queryset = queryset_bucket_specific_user(user.id)
        bucket_total_price = queryset.first().bucket_total_price
    bucket_total_price -= cashback_payment
    user_cashback -= cashback_payment
    user.amount_accrued_cashback = user_cashback
    user.save()
    return bucket_total_price, user_cashback
