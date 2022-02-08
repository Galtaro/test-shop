from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Item(models.Model):
    title = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to="%Y/%m/%d")


class Bucket(models.Model):
    items = models.ManyToManyField(Item)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

