from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField,\
    Serializer, IntegerField, CharField, DecimalField
from product.models import Item, Bucket, Promocode, BucketItems


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
    total_price = DecimalField(max_digits=7, decimal_places=2)
    count = IntegerField(source="count_")
    id = IntegerField(source="bucketitem_id")

    class Meta:
        model = Item
        exclude = ["image"]
        extra_fields = ["count", "id"]


class BucketSerializer(ModelSerializer):
    items = BucketItemSerializer(many=True)
    total_price = DecimalField(max_digits=7, decimal_places=2, source="bucket_total_price")

    class Meta:
        model = Bucket
        exclude = ["id", "last_modified", "owner"]
        extra_fields = ["total_price"]


class AddBucketSerializer(Serializer):
    count = IntegerField()


class RetrieveItemBucketSerializer(ModelSerializer):
    price_include_discount = DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = Item
        fields = ["title", "description", "price", "image", "price_include_discount"]


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
