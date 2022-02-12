from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField,\
    Serializer, IntegerField, CharField, DecimalField
from product.models import Item, Bucket


class ListItemSerializer(HyperlinkedModelSerializer):
    detail = HyperlinkedIdentityField("Product:retrieve-item")

    class Meta:
        model = Item
        fields = ["title", "price", "detail"]


class RetrieveItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]


class BucketItemSerializer(ModelSerializer):
    total_price = DecimalField(max_digits=5, decimal_places=2)
    count = IntegerField()

    class Meta:
        model = Item
        fields = ["id", "title", "description", "total_price", "count"]


class BucketSerializer(ModelSerializer):
    items = BucketItemSerializer(many=True)

    class Meta:
        model = Bucket
        fields = ["items"]


class AddBucketSerializer(Serializer):
    count = IntegerField()


class RetrieveItemBucketSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]


class UpdateBucketItemSerializer(Serializer):
    count = IntegerField()
