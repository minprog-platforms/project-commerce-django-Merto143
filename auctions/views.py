from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Auction_item, Bid, Comment, Category


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
    """Laadt de home-pagina, hier worden alle actieve
    listingen getoond. En kun je filteren op categorie."""

    # zorg dat de current_price goed wordt weergeven.
    update_higest_bids()

    categories = Category.objects.all()
    list_items = Auction_item.objects.all()

    # check of er een post binnenkomt
    if request.method == "POST":

        # sla de categorie van de post op
        Cat = request.POST["Category"]

        # check of er een categorie is opgegeven
        if Cat != "0":
            # update de list_items zodat alleen de item van met de opgegeven
            # categorie erin zitten
            list_items = Auction_item.objects.filter(Cat_item=Cat)

    return render(request, "auctions/index.html", {
        "items": list_items, "categories": categories})


def listing(request, item_id):
    """Laadt de listing pagina van het aangeklikte item. Hier kun je
    zien welke biedingen er zijn gedaan en ook comments plaatsen
    """
    item = Auction_item.objects.get(pk=item_id)
    bid_form = ""
    comment_form = ""
    watchlist = ""
    winner = ""

    if request.user.is_authenticated:

        # plaats form velden als de gebruiker ingelogd is
        bid_form = BidForm()
        comment_form = CommentForm()
        watchlist = request.user.Watch_item.all()

        # check of de gebruiker een form invult
        if request.method == "POST":
            bid_form = BidForm(request.POST)
            comment_form = CommentForm(request.POST)

            # check of de bidform is ingevuld
            if bid_form.is_valid():
                bid_price = request.POST["bid_price"]

                # check of de bieding hoog genoeg is
                check = check_bid(item, bid_price)

                # geef een error message als de biedin niet hoog genoeg is
                if check == 1:
                    messages.error(request,
                                   "Bid must be higher than item price")
                    return HttpResponseRedirect(reverse("listing",
                                                kwargs={'item_id': item.id}))
                elif check == 2:
                    messages.error(request,
                                   "Bid must be higher than other bids")
                    return HttpResponseRedirect(reverse("listing",
                                                kwargs={'item_id': item.id}))

                # maak een bieding
                new_bid = Bid(
                    bid_price=bid_price,
                    bidder=request.user
                )

                # check of de bieder niet ook de eigenaar van het item is
                if new_bid.bidder == item.owner:
                    messages.error(request,
                                   "You can't place any bids on your own item")
                    return HttpResponseRedirect(reverse("listing",
                                                kwargs={'item_id': item.id}))

                new_bid.save()
                new_bid.item.add(item)

                # het item wordt gelijk aan de wachtlist toevoegd als de
                # gebruiker op het item heeft geboden
                item.watchlist.add(request.user)

            # check of er een comment wordt geplaatst
            if comment_form.is_valid():
                comment_input = request.POST["comment_input"]

                # maak een niewe comment aan
                new_comment = Comment(
                    comment_input=comment_input,
                    commenter=request.user,
                )
                new_comment.save()
                new_comment.item.add(item)

        # krijg de winnaar van de veilig als het item niet meer actief is
        if not item.is_active:
            winner = get_winner(item)

    return render(request, "auctions/listing.html", {
        "item": item,
        "owner": item.owner,
        "bid_form": bid_form,
        "watchlist": watchlist,
        "bids": item.Bid_item.all(),
        "comment_form": comment_form,
        "comments": item.Comment.all(),
        "winner": winner,
        })


def create_listing(request):
    """Laadt de create listing pagina, waar de gebruiker een
    nieuwe veiling kan starten"""

    # plaats de form velden
    form = ListingForm()
    Categories = Category.objects.all()

    # check of de gebruiker de form goed heeft ingevuld
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            item_name = request.POST["item"]
            price = request.POST["price"]
            Img_url = request.POST["Img_url"]
            description = request.POST["description"]
            owner = request.user
            category = request.POST["Category"]

            # maak een new_listing item
            new_listing = Auction_item(
                item=item_name,
                price=price,
                Img_url=Img_url,
                description=description,
                owner=owner
            )

            new_listing.save()

            # als er een category opgegeven voegen we deze toe aan het item
            if category != "0":
                new_listing.Cat_item.add(category)

            # laadt de pagina voor het nieuwe item
            return HttpResponseRedirect(reverse("listing",
                                        kwargs={'item_id': new_listing.id}))

    return render(request, "auctions/create_listing.html",
                  {'form': form, 'categories': Categories})


@login_required
def my_watchlist(request):
    """Laadt my_watchlist pagina. Hier staan alle items die de
    gebruiker aan zijn/haar watchlist heeft toegevoegd"""

    watchlist = request.user.Watch_item.all()

    return render(request, "auctions/my_watchlist.html",
                  {"watchlist": watchlist})


@login_required
def add_to_watchlist(request, item_id):
    """Voegt een item toe aan de gebruikers watchlist en laadt
    vervolgens dezelfde listing pagina"""

    user = request.user
    item = Auction_item.objects.get(pk=item_id)

    # voeg het item toe aan de watchlist van de gebruiker
    item.watchlist.add(user)

    return HttpResponseRedirect(reverse("listing",
                                kwargs={'item_id': item.id}))


@login_required
def remove_from_watchlist(request, item_id):
    """Haalt een item van de gebruikers watchlist af en laadt
    vervolgens dezelfde listing pagina"""
    user = request.user
    item = Auction_item.objects.get(pk=item_id)

    # verwijder het item van de watchlist van de gebruiker
    item.watchlist.remove(user)

    return HttpResponseRedirect(reverse("listing",
                                kwargs={'item_id': item.id}))


@login_required
def my_listings(request):
    """Laadt de my_listings pagina. Deze pagina weergeeft alle listings van
    die de gebruiker zelf heeft geplaatst"""

    user = request.user
    userlistings = Auction_item.objects.filter(owner=user)

    return render(request, "auctions/my_listings.html",
                  {"listings": userlistings})


@login_required
def close_auction(request, item_id):
    item = Auction_item.objects.get(pk=item_id)
    item.is_active = False
    item.save()

    return HttpResponseRedirect(reverse("listing",
                                kwargs={'item_id': item.id}))


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
    """Log de gebruiker uit en laadt de index pagina"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """Laadt de register pagina waar de gebruiker een account kan aanmaken"""

    # check of de form wordt gesubmit
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
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password,
                                            first_name=first_name,
                                            last_name=last_name)
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
    """ Returns 0 if the bid placed is valid"""
    prices = []
    # check if bid is higher than starting price
    if float(bid_price) < item.price:
        return 1

    for bid in item.Bid_item.all():
        prices.append(bid.bid_price)

    if prices != []:
        max_bid = max(prices)

        # check if bid is higher than previous bids
        if float(bid_price) <= max_bid:
            return 2
    else:
        return 0


def get_winner(item):
    """Returnt hoogste bieder als de veilig is afgelopen, return een lege
    string als er niet op de veiling geboden is"""

    # check of er geboden is op het item
    if item.Bid_item.first() is not None:
        # de hoogste bieder is automatisch de laatste bieder
        winner = item.Bid_item.last().bidder.username
    else:
        winner = ""
    return winner
    

def update_higest_bids():
    """Update voor elke listing de hoogste bieding. Als deze er niet is
    de beginprijs."""

    for item in Auction_item.objects.all():
        # check of er een bieding op op het item
        if item.Bid_item.first() is None:
            item.highest_bid = item.price
        else:
            item.highest_bid = item.Bid_item.last().bid_price
        item.save()
    return
