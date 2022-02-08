from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, ListAPIView
from product.serializers import ListItemSerializer, RetrieveItemSerializer
from product.models import Item


class ListApiItem(ListAPIView):
    serializer_class = ListItemSerializer
    queryset = Item.objects.all()


class RetrieveApiItem(RetrieveAPIView):
    serializer_class = RetrieveItemSerializer
    queryset = Item.objects.all()
