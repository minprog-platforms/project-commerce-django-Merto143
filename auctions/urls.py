from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:item_id>", views.listing, name="listing"),
    path("create", views.create_listing, name="create"),
    path("add_watchlist/<int:item_id>", views.add_to_watchlist, name="watchlist"),
    path("my_watchlist", views.my_watchlist, name="my_watchlist")
]
