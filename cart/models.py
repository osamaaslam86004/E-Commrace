from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from Homepage.models import CustomUser


class Cart(models.Model):
    user = models.ForeignKey(
        CustomUser, blank=True, null=True, on_delete=models.CASCADE
    )
    subtotal = models.FloatField(default=0.00)
    total = models.FloatField(default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0.00)
