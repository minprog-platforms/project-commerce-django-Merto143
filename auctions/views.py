from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, Auction_item, Bid


class ListingForm(forms.ModelForm):
    class Meta:
        model = Auction_item
        labels = {"item": "Name"}
        fields = ['item', 'price', 'Img_url', 'description']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_price']

def index(request):
    return render(request, "auctions/index.html", {
        "items": Auction_item.objects.all()})

def listing(request, item_id):
    item = Auction_item.objects.get(pk = item_id)
    bid_form = ""
    if request.user.is_authenticated:
        bid_form = BidForm()

        if request.method == "POST":
            bid_form = BidForm(request.POST)

            if bid_form.is_valid():
                new_bid = bid_form.save()
                new_bid.bidder.add(request.user.id)
                new_bid.item.add(item)

    return  render(request, "auctions/listing.html", {
        "item": item,
        "owner": item.owner,
        "bid_form":bid_form
        })

def create_listing(request):
    form = ListingForm()

    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            item_name = request.POST["item"]
            price = request.POST["price"]
            Img_url = request.POST["Img_url"]
            description = request.POST["description"]
            owner = request.user
            new_listing = Auction_item(
                item=item_name,
                price=price,
                Img_url=Img_url,
                description=description,
                owner=owner
            )
            new_listing.save()

            return HttpResponseRedirect(reverse("listing", kwargs={'item_id': new_listing.id}))

        else:
            return HttpResponse("Niet gelukt")

    return render(request, "auctions/create_listing.html", {'form':form})

@login_required
def my_watchlist(request):
    watchlist = request.user.Watch_item.all()
    return render(request, "auctions/my_watchlist.html", {"watchlist": watchlist})

@login_required
def add_to_watchlist(request, item_id):
    user = request.user
    item = Auction_item.objects.get(pk = item_id)
    item.watchlist.add(user)
    return HttpResponse("Successful")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username = username, email = email, password = password, first_name = first_name, last_name = last_name)
            user.save()
            # user.first_name = first_name
            # user.last_name = last_name
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
