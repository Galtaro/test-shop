from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, HyperlinkedIdentityField
from product.models import Item


class ListItemSerializer(HyperlinkedModelSerializer):
    detail = HyperlinkedIdentityField("Product:retrieve-item")

    class Meta:
        model = Item
        fields = ["title", "price", "detail"]


class RetrieveItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ["title", "description", "price", "image"]