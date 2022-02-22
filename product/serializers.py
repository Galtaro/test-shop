from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField,\
    Serializer, IntegerField, CharField, DecimalField
from product.models import Item, Bucket, Promocode, BucketItems, Cashback


class ListItemSerializer(HyperlinkedModelSerializer):
    detail = HyperlinkedIdentityField("Product:retrieve-item")
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = Item
        fields = ["id", "title", "price", "price_include_discount", "detail"]


class RetrieveItemSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]


class AddItemSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]


class UpdateItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ("title", "description", "price", "image")


class BucketItemSerializer(ModelSerializer):
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)
    total_price_item = DecimalField(max_digits=7, decimal_places=2)
    count = IntegerField()
    bucketitem_id = IntegerField()

    class Meta:
        model = Item
        fields = ["bucketitem_id", "title", "price", "discount_percent", "price_include_discount", "count", "total_price_item"]


class BucketSerializer(ModelSerializer):
    items = BucketItemSerializer(many=True)
    total_price = DecimalField(max_digits=7, decimal_places=2, source="bucket_total_price")
    amount_accrued_cashback = DecimalField(max_digits=7, decimal_places=2, source="amount_accrued_cashback_")

    class Meta:
        model = Bucket
        exclude = ["id", "last_modified", "owner"]
        extra_fields = ["total_price", "amount_accrued_cashback"]


class AddBucketSerializer(Serializer):
    count = IntegerField()


class RetrieveItemBucketSerializer(ModelSerializer):
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)
    title = CharField(max_length=20)
    description = CharField(max_length=500)
    price = DecimalField(max_digits=7, decimal_places=2)
    discount_percent = IntegerField()
    total_price_item = DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = BucketItems
        fields = ["title", "description", "price", "discount_percent", "price_include_discount", "count", "total_price_item"]


class UpdateBucketItemsSerializer(ModelSerializer):
    item_id = IntegerField(read_only=True)

    class Meta:
        model = BucketItems
        fields = ["count", "item_id"]


class AddDiscountSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["discount_percent"]


class PromocodeSerializer(ModelSerializer):

    class Meta:
        model = Promocode
        fields = "__all__"


class AddPromocodeSerializer(ModelSerializer):

    class Meta:
        model = Promocode
        exclude = ["id"]


class UpdatePromocodeSerializer(ModelSerializer):

    class Meta:
        model = Promocode
        exclude = ["id"]


class UpdateBucketPromocodeTotalPriceSerializer(Serializer):
    promocode = CharField(max_length=8, allow_blank=False)


class CashbackSerializer(ModelSerializer):

    class Meta:
        model = Cashback
        fields = "__all__"


class AddCashbackSerializer(ModelSerializer):

    class Meta:
        model = Cashback
        fields = ["min_order_amout", "cashback_percent"]

class UpdateCashbackSerializer(ModelSerializer):

    class Meta:
        model = Cashback
        exclude = ["id"]


class CheckoutSerializer(Serializer):
    total_price = DecimalField(max_digits=7, decimal_places=2, source="bucket.bucket_total_price", read_only=True)


class BucketTotalPriceSerialzer(Serializer):
    bucket_total_price = DecimalField(max_digits=7, decimal_places=2)


class CashbackPaymentSerializer(Serializer):
    cashback_payment = DecimalField(max_digits=8, decimal_places=4)
