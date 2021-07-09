from django.contrib import admin
from .models import User, Listing, Watchlist, Bid, Comment, Category

# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
