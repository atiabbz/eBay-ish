from . import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from . import models
from . import utils
from datetime import datetime
from django.contrib.auth.decorators import login_required

from .models import User
from auctions import models


def index(request):
    listings = models.Listing.objects.filter(isActive=True)
    return render(request, "auctions/index.html", {
        'listings': listings
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
        # email = request.POST["email"]
        email = ''

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
def new(request):
    if request.method == 'POST':
        form = forms.NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            imageURL = form.cleaned_data['imageURL']
            category = form.cleaned_data['category']
            creator = request.user
            newListing = models.Listing(title=title, description=description, price=price, imageURL=imageURL, category=category, creator=creator)
            newListing.save()
            return HttpResponseRedirect(reverse('index'))
    newListingForm = forms.NewListingForm()
    return render(request, 'auctions/new.html', {
        'form': newListingForm
    })

def categories(request):
    categories = utils.getCategories()
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })

def category(request, category):
    if category not in utils.getCategories():
        return render(request, 'auctions/error.html')
    listings = models.Listing.objects.filter(category=category, isActive=True)
    return render(request, 'auctions/category.html', {
        'category': category.capitalize(),
        'listings': listings
    })

def listing(request, title, listing_id):
    listing = models.Listing.objects.get(id=listing_id)
    isValidBid = False
    isWatchlisted = False
    isCreator = (request.user == listing.creator)
    lastBid = models.Bid.objects.filter(listing=listing).last()
    isWinner = False
    if lastBid:
        isWinner = not listing.isActive and (lastBid.bidder == request.user)

    if request.method == 'POST':
        if request.POST['submit'] == 'Post':
            postedComment = forms.NewCommentForm(request.POST)
            if postedComment.is_valid():
                commenter = request.user
                content = postedComment.cleaned_data['content']
                comment = models.Comment(commenter=commenter,
                                        listing=listing,
                                        content=content,
                                        time=datetime.now())
                comment.save()
        if request.POST['submit'] == 'Bid':
            postedBid = forms.NewBidForm(request.POST)
            if postedBid.is_valid():
                bidder = request.user
                amount = postedBid.cleaned_data['amount']
                if amount > listing.price:
                    isValidBid = True
                    listing.price = amount
                    listing.save()
                    bid = models.Bid(bidder=bidder, listing=listing, amount=amount)
                    bid.save()

        if request.POST['submit'] == '🧐 Watch':
            listing.watchers.add(request.user)
            listing.save()

        if request.POST['submit'] == '😴 Unwatch':
            listing.watchers.remove(request.user)
            listing.save()

        if request.POST['submit'] == '🛑 Close':
            listing.isActive = False
            listing.save()

    bidForm = forms.NewBidForm()
    commentForm = forms.NewCommentForm()
    allComments = models.Comment.objects.filter(listing_id=listing_id).order_by('-time')

    if request.user.is_authenticated and listing in models.Listing.objects.filter(watchers=request.user):
        isWatchlisted = True

    return render(request, 'auctions/listing.html', {
        'listing': models.Listing.objects.get(id=listing_id),
        'bidForm': bidForm,
        'commentForm': commentForm,
        'isValidBid': isValidBid,
        'allComments': allComments,
        'isWatchlisted': isWatchlisted,
        'isCreator': isCreator,
        'isActive': listing.isActive,
        'isWinner': isWinner
    })


@login_required
def watchlist(request):
    watchlist = request.user.watchlisted_listings.all()
    return render(request, 'auctions/watchlist.html', {
        'watchlist': watchlist
    })


@login_required
def bids(request):
    bidsNotDistinct = request.user.bids.all()

    # janky ass distinct listings finding cuz sqlite3 can't do it
    bids = []
    listing_ids = set()
    for bid in bidsNotDistinct:
        if bid.listing_id not in listing_ids:
            bids.append(bid)
            listing_ids.add(bid.listing_id)

    return render(request, 'auctions/bids.html', {
        'bids': bids
    })

def myListings(request):
    myListings = request.user.created_listings.all()
    return render(request, 'auctions/my-listings.html', {
        'myListings': myListings
    })