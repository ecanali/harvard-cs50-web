from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Watchlist, Bid, Comment, Category


# Form fields:
class CreateListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class':'form-control'}))
    description = forms.CharField(label="Description", widget=forms.TextInput(attrs={'class':'form-control'}))
    starting_price = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'placeholder':'0', 'class':'form-control'}))
    image_url = forms.URLField(widget=forms.TextInput(attrs={'placeholder':'http://', 'class':'form-control'}), label='Image URL', required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Choose one", widget=forms.Select(attrs={'class':'form-control'}))


class CreateBidForm(forms.Form):
    bid = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'placeholder':'0', 'class':'form-control reduced-inputs'}))


class CreateCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Write your comment here', "rows":2, "cols":30, 'class':'form-control'}), required=False)


# Routes:
@login_required(redirect_field_name=None, login_url='/login')
def create(request):
    form = CreateListingForm(request.POST or None)
    user = User.objects.get(id=request.user.id)
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, 'Sorry, you must log in before create a listing.')
            return HttpResponseRedirect(reverse("create"))
        if form.is_valid():
            # Isolate the data from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_price = form.cleaned_data["starting_price"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data['category']

            listing = Listing(
                title=title, 
                description=description, 
                starting_price=starting_price, 
                current_price=starting_price, 
                image_url=image_url, 
                category_id=Category.objects.get(name=category.name), 
                status="active", 
                owner_user_id=User.objects.get(id=user.id), 
                winner_id=User.objects.get(id=user.id)
            )
            listing.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    else:
        return render(request, "auctions/create.html", {
        "form": form
    })


def index(request):
    return render(request, "auctions/index.html", {
        "active_listing": Listing.objects.filter(status="active").order_by('-id')
    })


def listing(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        messages.error(request, 'Sorry, listing does not exist.')
        return HttpResponseRedirect(reverse("index"))

    watchlisted = False
    owner = False
    winner = False

    comments = Comment.objects.filter(listing_id=listing).order_by('-id')

    bid_form = CreateBidForm(request.POST or None)
    comment_form = CreateCommentForm(request.POST or None)

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)

        if user.username == str(listing.owner_user_id):
            owner = True
            
        if user == listing.winner_id and user != listing.owner_user_id:
            winner = True
        
        user_watchlist = Watchlist.objects.get(user_id=user.id)

        converted_watchlist = user_watchlist.listings_watched.strip('"[]"').split(', ')

        for item in converted_watchlist:
            if str(id) == item:
                watchlisted = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlisted": watchlisted,
        "owner": owner,
        "winner": winner,
        "comments": comments,
        "bid_form": bid_form,
        "comment_form": comment_form
    })


@login_required(redirect_field_name=None, login_url='/login')
def watch(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        messages.error(request, 'Sorry, listing does not exist.')
        return HttpResponseRedirect(reverse("index"))

    user = User.objects.get(id=request.user.id)
    user_watchlist = Watchlist.objects.get(user_id=user.id)

    converted_watchlist = user_watchlist.listings_watched.strip('"[]"').split(', ')

    string_watchlist = ""
    separator = ", "
    for item in converted_watchlist:
        if str(id) == item:
            converted_watchlist.remove(item)
            string_watchlist = separator.join(converted_watchlist)
            user_watchlist.listings_watched = string_watchlist
            user_watchlist.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        if not str(id) in converted_watchlist:
            # When user has no watchlist because removed all items by itself:
            if len(converted_watchlist) == 1 and item == "":
                converted_watchlist.append(str(id))
                separator2 = ""
                string_watchlist = separator2.join(converted_watchlist)
                user_watchlist.listings_watched = string_watchlist
                user_watchlist.save()
                return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
            converted_watchlist.append(str(id))
            string_watchlist = separator.join(converted_watchlist)
            user_watchlist.listings_watched = string_watchlist
            user_watchlist.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required(redirect_field_name=None, login_url='/login')
def bid(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        messages.error(request, 'Sorry, listing does not exist.')
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        bid_form = CreateBidForm(request.POST or None)

        if bid_form.is_valid():
            # Isolate the data from the 'cleaned' version of form data
            bid_offered = bid_form.cleaned_data["bid"]

            if bid_offered > listing.current_price:
                new_bid = Bid(price=bid_offered, listing_id=listing, user_id=User.objects.get(id=request.user.id))
                new_bid.save()
                listing.current_price = bid_offered
                listing.save()
                messages.success(request, 'Congratulations, now you have the highest bid.')
                return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
            else:
                messages.error(request, 'Sorry, bid must be greater than the current price.')
                return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            messages.error(request, 'Sorry, invalid bid.')
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required(redirect_field_name=None, login_url='/login')
def close(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        messages.error(request, 'Sorry, listing does not exist.')
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        user = User.objects.get(id=request.user.id)
        if not user.username == str(listing.owner_user_id):
            messages.error(request, 'Sorry, you are not the owner of this listing.')
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        
        listing_bids = Bid.objects.filter(listing_id=listing.id).order_by('-price')
        winner_user = User.objects.get(username=listing_bids[0].user_id)

        listing.status = "closed"
        listing.winner_id = winner_user
        listing.save()

        messages.success(request, 'Alright! You have closed this listing and declared the last bidder the winner!')
            
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required(redirect_field_name=None, login_url='/login')
def comment(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        messages.error(request, 'Sorry, listing does not exist.')
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        user = User.objects.get(id=request.user.id)

        comment_form = CreateCommentForm(request.POST or None)

        if comment_form.is_valid():
            new_comment = Comment(text=comment_form.cleaned_data["comment"], listing_id=listing, user_id=user)
            new_comment.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
        else:
            messages.error(request, 'Sorry, invalid comment.')
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


@login_required(redirect_field_name=None, login_url='/login')
def watchlist(request):
    user = User.objects.get(id=request.user.id)
    user_watchlist = Watchlist.objects.filter(user_id=user.id)

    if user_watchlist[0].listings_watched == "":
        messages.error(request, 'Sorry, you do not have any listing in your watchlist yet.')
        return HttpResponseRedirect(reverse("index"))

    converted_watchlist = user_watchlist[0].listings_watched.strip('"[]"').split(', ')

    list_listing_ids = []
    for item in converted_watchlist:
        item = int(item)
        list_listing_ids.append(item)

    listings_watched = Listing.objects.filter(pk__in=list_listing_ids).order_by('-id')
    
    return render(request, "auctions/watchlist.html", {
        "active_listing": listings_watched
    })


def categories(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        if filter == "all":
            return render(request, "auctions/categories.html", {
                "active_listing": Listing.objects.filter(status="active").order_by('-id'),
                "categories": Category.objects.all()
            })
        else:
            return render(request, "auctions/categories.html", {
                "filter": int(filter),
                "active_listing": Listing.objects.filter(category_id=int(filter), status="active"),
                "categories": Category.objects.all()
            })
    else:
        return render(request, "auctions/categories.html", {
            "active_listing": Listing.objects.filter(status="active").order_by('-id'),
            "categories": Category.objects.all()
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
