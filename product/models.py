from django.core import validators
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Item(models.Model):
    title = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(upload_to="%Y/%m/%d")

    objects = models.Manager()

    def __str__(self):
        return str(self.title)


class Bucket(models.Model):
    items = models.ManyToManyField(
        Item,
        related_name="item_bucket",
        through="product.BucketItems"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class BucketItems(models.Model):
    count = models.PositiveIntegerField(
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100)])
    bucket = models.ForeignKey(
        Bucket,
        on_delete=models.CASCADE,
        related_name="bucket_items_bucket"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="bucket_items_item"
    )

    objects = models.Manager()


class Promocode(models.Model):
    name = models.CharField(max_length=8,)
    promocode_discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100)]
    )
    promocode_summ_discount = models.BooleanField(default=False)

    objects = models.Manager()


class Cashback(models.Model):
    min_order_amount = models.PositiveIntegerField(
        default=0,
        validators=[validators.MinValueValidator(0)]
    )
    cashback_percent = models.PositiveIntegerField(
        default=0,
        validators=[validators.MinValueValidator(0)]
    )
    last_modified = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class UseCashbackAmount(models.Model):
    min_amount_use_cashback = models.PositiveIntegerField(
        default=0,
        validators=[validators.MinValueValidator(0)]
    )
    last_modified = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class EmailDeliveryNotification(models.Model):
    hour_before_delivery = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=60)

    objects = models.Manager()

    def __str__(self):
        if self.hour_before_delivery is None:
            return "---"
        return str(self.title)


class Order(models.Model):

    account = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="order_user"
    )
    order_sum = models.DecimalField(max_digits=6, decimal_places=2)
    order_date = models.DateField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    delivery_date_time = models.DateTimeField(null=True)
    email_delivery_notification = models.ForeignKey(
        EmailDeliveryNotification,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name="order_emaildeliverynotification"
    )

    objects = models.Manager()


class PromotionalOffer(models.Model):
    promotional_item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="promotional_offer_item")
    discount_percent = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100)]
    )
    promotional_price = models.DecimalField(max_digits=6, decimal_places=2)
    validity = models.DateField()

    objects = models.Manager()
