from rest_framework.fields import ImageField
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField,\
    Serializer, IntegerField, CharField, DecimalField
from product.models import Item, Bucket, Discount


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


class UpdateItemSerializer(Serializer):
    title = CharField()
    description = CharField()
    price = DecimalField(max_digits=7, decimal_places=2)
    image = ImageField()


class BucketItemSerializer(ModelSerializer):
    total_price = DecimalField(max_digits=7, decimal_places=2)
    count = IntegerField(source="count_")

    class Meta:
        model = Item
        exclude = ["image"]
        extra_fields = ["count"]


class BucketSerializer(ModelSerializer):
    items = BucketItemSerializer(many=True)
    total_price = IntegerField(source="bucket_total_price")  # TODO replace on DecimalField

    class Meta:
        model = Bucket
        fields = "__all__"  # TODO add exclude
        extra_fields = ["total_price"]


class AddBucketSerializer(Serializer):
    count = IntegerField()


class RetrieveItemBucketSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]


class UpdateBucketItemSerializer(Serializer):
    count = IntegerField()


class AddDiscountSerializer(Serializer):
    discount_percent = IntegerField()