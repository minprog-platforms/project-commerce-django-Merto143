from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def __str__(self):

        return f"{self.first_name} {self.last_name}"


class Auction_item(models.Model):
    item = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="Auction_items")
    Img_url = models.CharField(max_length=250)
    description = models.TextField()
    watchlist = models.ManyToManyField(User, blank=True, related_name="Watch_item")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item}"


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="Bidder")
    item = models.ManyToManyField(Auction_item, related_name="Bid_item")
    bid_price = models.DecimalField(max_digits=12, decimal_places=2)

class Comment(models.Model):
    comment_input = models.TextField(max_length=250)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="Commenter")
    item = models.ManyToManyField(Auction_item, related_name="Comment")
