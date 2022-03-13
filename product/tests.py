from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from product.models import Item


class ItemTest(TestCase):

    def test_list_item(self):
        Item.objects.create(
            title="bread",
            description="the best bread ever",
            price=2.5,
            image="bread/img.jpg",
            discount_percent=0
        )
        Item.objects.create(
            title="fish",
            description="the fish bread ever",
            price=3,
            image="fish/img.jpg",
            discount_percent=0
        )
        response = self.client.get(reverse("Product:list-item"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


