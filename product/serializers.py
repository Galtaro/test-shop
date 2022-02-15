from rest_framework.fields import ImageField
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField,\
    Serializer, IntegerField, CharField, DecimalField
from product.models import Item, Bucket


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

    class Meta:
        model = Item
        exclude = ["image"]
        extra_fields = ["count"]


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


class UpdateBucketItemSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["count"]


class AddDiscountSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ["discount_percent"]
