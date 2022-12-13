from django.contrib import admin
from .models import User, Auction_item, Bid

# Register your models here.
admin.site.register(User)
admin.site.register(Auction_item)
admin.site.register(Bid)
