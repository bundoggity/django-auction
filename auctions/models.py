from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_user")
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=64)
    image = models.URLField()
    startbid = models.IntegerField(default=0)
    highestbid = models.IntegerField(default=0)
    CATEGORIES = (
        ('FA', 'Fashion'),
        ('TO', 'Toys'),
        ('EL', 'Electronics'),
        ('HO', 'Home'),
        ('OT', 'Other'),
    )
    category = models.CharField(max_length=2, choices=CATEGORIES, default='OT')
    isopen = models.BooleanField(default=True)


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction")
    bid = models.IntegerField()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    comment = models.CharField(max_length=64)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")
    items = models.ManyToManyField(Auction)