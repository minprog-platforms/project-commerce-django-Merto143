from django.contrib import admin
from .models import User, Auction_item, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Auction_item)
admin.site.register(Bid)
admin.site.register(Comment)
