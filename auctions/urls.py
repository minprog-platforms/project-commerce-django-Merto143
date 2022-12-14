from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:item_id>", views.listing, name="listing"),
    path("create", views.create_listing, name="create"),
    path("add_watchlist/<int:item_id>", views.add_to_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:item_id>", views.remove_from_watchlist, name="remove_watchlist"),
    path("my_watchlist", views.my_watchlist, name="my_watchlist"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("close_auction/<int:item_id>", views.close_auction, name="close_auction"),
]
