from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField,\
    Serializer, IntegerField, CharField, DecimalField
from rest_framework.exceptions import ValidationError

from datetime import timedelta
from django.utils.timezone import now

from product.models import Item, Bucket, Promocode, BucketItems, Cashback, UseCashbackAmount, EmailDeliveryNotification, \
    Order, PromotionalOffer


class ListItemSerializer(HyperlinkedModelSerializer):
    detail = HyperlinkedIdentityField("Product:retrieve-item")
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)
    discount_percent = IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Item
        fields = ["id", "title", "price", "discount_percent", "price_include_discount", "detail"]


class RetrieveItemSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["title", "description", "image"]


class CreateItemSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]


class UpdateItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ("title", "description", "price", "image")


class ListBucketItemSerializer(ModelSerializer):
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)
    total_price_item = DecimalField(max_digits=7, decimal_places=2)
    count = IntegerField()
    bucketitem_id = IntegerField()

    class Meta:
        model = Item
        fields = ["bucketitem_id", "title", "price", "discount_percent", "price_include_discount", "count", "total_price_item"]


class ListBucketSerializer(ModelSerializer):
    items = ListBucketItemSerializer(many=True)
    total_price = DecimalField(
        max_digits=7,
        decimal_places=2,
        source="bucket_total_price"
    )
    amount_accrued_cashback = DecimalField(
        max_digits=7,
        decimal_places=2,
        source="amount_accrued_cashback_"
    )

    class Meta:
        model = Bucket
        exclude = ["id", "last_modified", "owner"]
        extra_fields = ["total_price", "amount_accrued_cashback"]


class CreateBucketItemSerializer(Serializer):
    count = IntegerField(min_value=1)


class RetrieveItemBucketSerializer(ModelSerializer):
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)
    title = CharField(max_length=20)
    description = CharField(max_length=500)
    price = DecimalField(max_digits=7, decimal_places=2)
    discount_percent = IntegerField()
    total_price_item = DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = BucketItems
        fields = [
            "title", "description", "price", "discount_percent", "price_include_discount", "count", "total_price_item"
        ]


class UpdateBucketItemsSerializer(ModelSerializer):
    id = IntegerField(read_only=True)

    class Meta:
        model = BucketItems
        fields = ["count", "id"]


class UpdateDiscountSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["discount_percent"]


class ListPromocodeSerializer(ModelSerializer):

    class Meta:
        model = Promocode
        fields = "__all__"


class CreatePromocodeSerializer(ModelSerializer):

    class Meta:
        model = Promocode
        exclude = ["id"]


class UpdatePromocodeSerializer(ModelSerializer):

    class Meta:
        model = Promocode
        exclude = ["id"]


class UpdateBucketPromocodeTotalPriceSerializer(Serializer):
    promocode = CharField(max_length=8, allow_blank=False)

    def validate(self, attrs):
        promocode = self.initial_data["promocode"]
        promocode_query = Promocode.objects.filter(name=promocode)
        if not promocode_query.exists():
            raise ValidationError({
                "detail": "This promo code is not valid"
            }, code='invalid')
        return attrs


class ListCashbackSerializer(ModelSerializer):

    class Meta:
        model = Cashback
        fields = "__all__"


class CreateCashbackSerializer(ModelSerializer):

    class Meta:
        model = Cashback
        fields = ["min_order_amout", "cashback_percent"]


class UpdateCashbackSerializer(ModelSerializer):

    class Meta:
        model = Cashback
        exclude = ["id"]


class CreateCheckoutSerializer(ModelSerializer):
    total_price = DecimalField(
        max_digits=7,
        decimal_places=2,
        source="bucket.bucket_total_price",
        read_only=True
    )

    class Meta:
        model = Order
        fields = ["delivery_date_time", "email_delivery_notification", "total_price"]

    def validate(self, attrs):
        min_time_delivery = now() + timedelta(hours=3)
        delivery_date_time = attrs["delivery_date_time"]
        if delivery_date_time < min_time_delivery:
            raise ValidationError(detail="enter valid delivery time")
        email_delivery_notification = attrs["email_delivery_notification"]
        queryset = EmailDeliveryNotification.objects.filter(
            hour_before_delivery=email_delivery_notification.hour_before_delivery
        )
        if not queryset:
            raise ValidationError(detail="enter valid notification delivery time")
        return attrs


class CashbackPaymentSerializer(Serializer):
    cashback_payment = DecimalField(max_digits=8, decimal_places=4, min_value=0)

    def validate(self, attrs):
        cashback_payment = int(self.initial_data["cashback_payment"])
        min_amount_use_cashback = UseCashbackAmount.objects.first().min_amount_use_cashback
        user = self.context.get('request').user
        user_cashback = user.amount_accrued_cashback
        if user_cashback < min_amount_use_cashback:
            raise ValidationError(
                {"detail": "The amount of accrued cashback is less than the minimum usage threshold"},
                code='invalid'
            )
        if user_cashback < cashback_payment:
            raise ValidationError(
                {"detail": "The amount of cashback withdrawn is greater than the amount of the account balance. \
                Try again"},
                code='invalid')
        return attrs


class CreatePromotionalOfferSerializer(ModelSerializer):

    class Meta:
        model = PromotionalOffer
        fields = ["promotional_item", "discount_percent", "validity"]


class UpdateDestroyPromotionalOfferSerializer(ModelSerializer):

    class Meta:
        model = PromotionalOffer
        fields = "__all__"
