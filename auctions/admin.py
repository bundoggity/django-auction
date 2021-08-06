from django.contrib import admin
from .models import User, Auction, Bid, Watchlist, Comment
# Register your models here.

admin.site.register(User)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Watchlist)
admin.site.register(Comment)