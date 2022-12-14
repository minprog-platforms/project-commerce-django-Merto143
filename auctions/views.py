from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Auction_item, Bid, Comment


class ListingForm(forms.ModelForm):
    class Meta:
        model = Auction_item
        labels = {"item": "Name"}
        fields = ['item', 'price', 'Img_url', 'description']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        labels = {"bid_price": "Place Bid: €"}
        fields = ['bid_price']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment_input"]

def index(request):
    return render(request, "auctions/index.html", {
        "items": Auction_item.objects.all()})

def listing(request, item_id):
    item = Auction_item.objects.get(pk = item_id)
    bid_form = ""
    comment_form = ""
    watchlist = ""

    if request.user.is_authenticated:
        bid_form = BidForm()
        comment_form = CommentForm()
        watchlist = request.user.Watch_item.all()

        if request.method == "POST":
            bid_form = BidForm(request.POST)
            comment_form = CommentForm(request.POST)

            if bid_form.is_valid():
                bid_price = request.POST["bid_price"]

                check = check_bid(item, bid_price)

                if check == 1:
                    messages.error(request, "Bid must be higher than item price")
                    return HttpResponseRedirect(reverse("listing", kwargs={'item_id': item.id}))
                elif check == 2:
                    messages.error(request, "Bid must be higher than other bids")
                    return HttpResponseRedirect(reverse("listing", kwargs={'item_id': item.id}))


                new_bid = Bid(
                    bid_price = bid_price,
                    bidder = request.user
                )

                new_bid.save()
                new_bid.item.add(item)

            if comment_form.is_valid():
                comment_input = request.POST["comment_input"]

                new_comment = Comment(
                    comment_input = comment_input,
                    commenter = request.user,
                )
                new_comment.save()
                new_comment.item.add(item)

    return  render(request, "auctions/listing.html", {
        "item": item,
        "owner": item.owner,
        "bid_form":bid_form,
        "watchlist": watchlist,
        "bids": item.Bid_item.all(),
        "comment_form": comment_form,
        "comments": item.Comment.all()
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
    return HttpResponseRedirect(reverse("listing", kwargs={'item_id': item.id}))

@login_required
def remove_from_watchlist(request, item_id):
    user = request.user
    item = Auction_item.objects.get(pk = item_id)
    item.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listing", kwargs={'item_id': item.id}))

@login_required
def my_listings(request):
    user = request.user
    userlistings = Auction_item.objects.filter(owner=user)
    return render(request, "auctions/my_listings.html", {"listings": userlistings})

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

def check_bid(item, bid_price):
    prices = []
    if float(bid_price) < item.price:
        return 1
    for bid in item.Bid_item.all():
        prices.append(bid.bid_price)
    if prices != []:
        max_bid = max(prices)
        if float(bid_price) <= max_bid:
            return 2
    else:
        return 0
