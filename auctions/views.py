from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Auction, Bid, Watchlist, Comment

class NewListing(forms.Form):
    title = forms.CharField(label="Listing name")
    description = forms.CharField(widget=forms.Textarea, label="Listing description")
    url = forms.URLField(label="Image link", required=False)
    category = forms.ChoiceField(choices=Auction.CATEGORIES)
    startbid = forms.IntegerField()

class NewBid(forms.Form):
    amount = forms.FloatField(label="Amount")

class CommentField(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)

class CategorySearch(forms.Form):
    category = forms.ChoiceField(choices=Auction.CATEGORIES)

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Auction.objects.all(),
        "category": CategorySearch(),
        "title": "Active Listings",
    })


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
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def createauction(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "forms": NewListing()
        })

    else:
        listing_data = NewListing(request.POST)
        if listing_data.is_valid():
            newauct = Auction(
                user=request.user,
                title=listing_data.cleaned_data["title"],
                description=listing_data.cleaned_data["description"],
                image=listing_data.cleaned_data["url"],
                startbid=listing_data.cleaned_data["startbid"],
                highestbid=listing_data.cleaned_data["startbid"]
            )
            newauct.save()
            
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html",{
                "forms": listing_data
            })

def listing(request, listing_id):
    auction = Auction.objects.get(id=listing_id)
    bids_for_auction = Bid.objects.all().filter(auction=auction).order_by("bid")
    total_bids = bids_for_auction.count()

    if total_bids > 0:
        top_bidder = bids_for_auction.last().user
        bidinfo = f"There are { total_bids } total bids. "
        if top_bidder.pk == request.user.pk:
            bidinfo += "You are the highest bidder"
    else:
        bidinfo = f"There are no current bids."
    
    watching = False
    if request.user.is_authenticated:
        if Watchlist.objects.filter(user=request.user).exists():
            watch = Watchlist.objects.get(user=request.user)
            if watch.items.filter(id=listing_id).exists():
                watching = True


    if request.method == "GET":
        if auction.isopen:
            return render(request, "auctions/listing.html", {
                "auction": auction,
                "form": NewBid(),
                "commentform": CommentField(),
                "bidinfo": bidinfo,
                "watching": watching,
                "comments": Comment.objects.all().filter(auction=auction)
            })

        else:
            if total_bids > 0:
                top_bid = bids_for_auction.last()
            else:
                top_bid = None

            return render(request, "auctions/listing.html", {
                "auction": auction,
                "top_bid": top_bid,
                "bidinfo": bidinfo,
                "watching": watching
            })
            

@login_required
def placebid(request, listing_id):
    newbid = NewBid(request.POST)
    if newbid.is_valid():
        bid_listing = Bid(
            bid = newbid.cleaned_data["amount"],
            user = request.user,
            auction = Auction.objects.get(id=listing_id)
        )

        if bid_listing.auction.highestbid < bid_listing.bid:
            bid_listing.auction.highestbid = bid_listing.bid
            bid_listing.save()
            bid_listing.auction.save()
            return HttpResponseRedirect(reverse("listing", args={listing_id}))
        else:
            err = f"You must bid more than {bid_listing.auction.highestbid}"
            return render(request, "auctions/listing.html" , {
                "error": err,
                "auction": bid_listing.auction,
                "form": NewBid(),
                "commentform": CommentField(),
                "bidinfo": bidinfo,
                "watching": watching
            })

def comment(request, listing_id):
    comment = CommentField(request.POST)
    if comment.is_valid():
        new_comment = Comment(
            user=request.user, 
            auction=Auction.objects.get(id=listing_id),
            comment=comment.cleaned_data['comment']
        )
        new_comment.save()
        return HttpResponseRedirect(reverse("listing", args={listing_id}))
    

@login_required
def add_to_watchlist(request, listing_id):
    listing = Auction.objects.get(pk=listing_id)
    if Watchlist.objects.filter(user=request.user).exists():
        user_watch = Watchlist.objects.get(user=request.user)
        if user_watch.items.filter(id=listing_id).exists():
            user_watch.items.remove(Auction.objects.get(id=listing_id))
        else:
            user_watch.items.add(Auction.objects.get(id=listing_id))
        user_watch.save()
    
    else:
        newindex = Watchlist.objects.create(user=request.user)
        newindex.items.add(Auction.objects.get(pk=listing_id))
        newindex.save()

    return HttpResponseRedirect(reverse("listing", args={listing_id}))



@login_required
def closelisting(request, listing_id):
    if request.method == "GET":
        auction_obj = Auction.objects.get(pk=listing_id)
        if request.user.pk == auction_obj.user.pk:
            auction_obj.isopen = False
            auction_obj.save()
            return HttpResponseRedirect(reverse("listing", args={listing_id}))

@login_required
def watchlist(request):
    if request.method == "GET":
        watchlist = Watchlist.objects.get(user=request.user)
        return render(request, "auctions/index.html", {
            "listings": watchlist.items.all(),
            "title": "Watchlist",
        })

def categories(request):
    if request.method == "GET":
        return  render(request, "auctions/categories.html", {
            "form": CategorySearch()
        })
    else:
        choice = request.POST['category']
        return render(request, "auctions/categories.html", {
            "form": CategorySearch(),
            "listings": Auction.objects.filter(category=choice).all(),
        })
