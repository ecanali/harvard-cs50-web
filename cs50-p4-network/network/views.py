import json
from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follower, Like


class CreatePostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "What's happening?", "rows":2, 'class':'form-control'}), required=True, label='')


def index(request):
    post_form = CreatePostForm(request.POST or None)
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        user = User.objects.get(id=request.user.id)

        if post_form.is_valid():
            post = Post(
                author=user, 
                content=post_form.cleaned_data["content"]
            )
            post.save()

            return HttpResponseRedirect(reverse("index"))
    else:
        # Pagination logic
        post_list = Post.objects.all().order_by('-id')
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get list of liked posts
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            posts_liked = Like.objects.filter(user=user)

            liked_posts = []
            for liked_post in posts_liked:
                liked_posts.append(liked_post.post.id)
            
            return render(request, "network/index.html", {
                "post_form": post_form,
                "page_obj": page_obj,
                "liked_posts": liked_posts
            })

        return render(request, "network/index.html", {
            "post_form": post_form,
            "page_obj": page_obj
        })


def profile_view(request, username):
    try:
        user = User.objects.get(username=username)

        # Pagination logic
        post_list = Post.objects.filter(author=user).order_by('-id') 
        paginator = Paginator(post_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if request.user.is_authenticated:
            try:
                current_user = User.objects.get(id=request.user.id)
                is_following = False

                if Follower.objects.filter(user=user, follower=current_user).exists():
                    is_following = True

                # Get list of liked posts
                posts_liked = Like.objects.filter(user=current_user)
                liked_posts = []
                for liked_post in posts_liked:
                    liked_posts.append(liked_post.post.id)

                return render(request, "network/profile.html", {
                    "page_obj": page_obj,
                    "followers": len(Follower.objects.filter(user=user)),
                    "following": len(Follower.objects.filter(follower=user)),
                    "user_profile": user,
                    "is_following": is_following,
                    "liked_posts": liked_posts
                })
            except User.DoesNotExist:
                return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "network/profile.html", {
                "page_obj": page_obj,
                "followers": len(Follower.objects.filter(user=user)),
                "following": len(Follower.objects.filter(follower=user)),
                "user_profile": user
            })

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))


@login_required(redirect_field_name=None, login_url='/login')
def following(request):
    current_user = User.objects.get(id=request.user.id)
    following = Follower.objects.filter(follower=current_user)

    posts = []
    for follow in following:
        following_user_posts = Post.objects.filter(author=follow.user)
        for post in following_user_posts:
            posts.append(post)

    def get_post_id(post):
        return post.id

    # Sort posts list by most recent
    posts.sort(reverse=True, key=get_post_id)

    # Pagination logic
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get list of liked posts
    posts_liked = Like.objects.filter(user=current_user)
    liked_posts = []
    for liked_post in posts_liked:
        liked_posts.append(liked_post.post.id)

    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "liked_posts": liked_posts
    })


@csrf_exempt
@login_required(redirect_field_name=None, login_url='/login')
def edit(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Ensure a user can't edit anyone's post
    user = User.objects.get(id=request.user.id)
    if user == post.author:

        # Update post content into database
        if request.method == "PUT":
            data = json.loads(request.body)

            if data.get("content") is not None:
                post.content = data["content"]

            post.save()

            return HttpResponse(status=204)

        # Email must be via PUT
        else:
            return JsonResponse({
                "error": "PUT request required."
            }, status=400)
    else:
        return HttpResponseRedirect(reverse("index"))


def follow(request, user_id):
    try:
        # Get current user and target user to follow/unfollow
        current_user = User.objects.get(id=request.user.id)
        target_user = User.objects.get(id=user_id)

        # Prevent user follows itself
        if current_user == target_user:
            return HttpResponseRedirect(reverse("index"))

        # Remove if already following, else add the follower
        if Follower.objects.filter(user=target_user, follower=current_user).exists():
            Follower.objects.filter(user=target_user, follower=current_user).delete()
        else:
            add_follower = Follower(
                user=target_user, 
                follower=current_user
            )
            add_follower.save()
    
        return HttpResponseRedirect(reverse("profile", args=(target_user.username,)))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))


@login_required(redirect_field_name=None, login_url='/login')
def like(request, post_id):
    
    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    current_user = User.objects.get(id=request.user.id)
    
    # Remove if already liking, else add the like
    if Like.objects.filter(user=current_user, post=post).exists():
        Like.objects.filter(user=current_user, post=post).delete()

        # Decrease post like counter
        post.likes -= 1 
        post.save()
    else:
        add_like = Like(
            user=current_user, 
            post=post
        )
        add_like.save()

        # Increase post like counter
        post.likes += 1 
        post.save()
        
    return HttpResponse(status=204)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
