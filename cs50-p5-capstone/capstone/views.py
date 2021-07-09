import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


from .models import User, Recipe, File


def index(request):
    recipes = Recipe.objects.all().order_by('-id')[:6]

    # Get only the first image to recipe cover display
    recipes_first_file = []
    for recipe in recipes:
        first_file = recipe.files.first()
        recipes_first_file.append(first_file)

    return render(request, "capstone/index.html", {
        'recipes': recipes,
        'files': recipes_first_file
    })


def about(request):
    return render(request, "capstone/about.html")


def recipes(request):
    # Pagination logic
    recipes_list = Recipe.objects.all().order_by('-id')
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get only the first image to recipe cover display
    recipes_first_file = []
    for recipe in recipes_list:
        first_file = recipe.files.first()
        recipes_first_file.append(first_file)

    return render(request, "capstone/recipes.html", {
        'page_obj': page_obj,
        'files': recipes_first_file
    })


def recipe(request, id):
    recipe = Recipe.objects.get(pk=id)

    return render(request, "capstone/recipe.html", {
        'recipe': recipe,
        'files': recipe.files.all(),
        'first_file': recipe.files.first()
    })


def filter(request):
    term = request.GET.get('filter')

    # Search all recipes that contains into its text the searched term 
    filtered_list = Recipe.objects.filter(
        Q(title__icontains=term) | 
        Q(chef__icontains=term) | 
        Q(ingredients__icontains=term) | 
        Q(preparation__icontains=term) | 
        Q(information__icontains=term)
    ).order_by('-id')

    # Prevent bug as of second page of pagination
    filtered = True

    # Get only the first image to recipe cover display
    recipes_first_file = []
    for recipe in filtered_list:
        first_file = recipe.files.first()
        recipes_first_file.append(first_file)

    return render(request, "capstone/recipes.html", {
        'page_obj': filtered_list,
        'files': recipes_first_file,
        'filtered': filtered
    })


@login_required(redirect_field_name=None, login_url='/admin/login')
def myrecipes(request):
    user = User.objects.get(pk=request.user.id)

    # Pagination logic
    recipes_list = Recipe.objects.filter(owner=user).order_by('-id')
    paginator = Paginator(recipes_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get only the first image to recipe cover display
    recipes_first_file = []
    for recipe in recipes_list:
        first_file = recipe.files.first()
        recipes_first_file.append(first_file)

    return render(request, "capstone/admin/recipes/index.html", {
        'page_obj': page_obj,
        'files': recipes_first_file
    })


@login_required(redirect_field_name=None, login_url='/admin/login')
def myrecipe(request, id):
    recipe = Recipe.objects.get(pk=id)

    return render(request, "capstone/admin/recipes/recipe.html", {
        'recipe': recipe,
        'files': recipe.files.all(),
        'first_file': recipe.files.first()
    })


@login_required(redirect_field_name=None, login_url='/admin/login')
def create_view(request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)

        recipe = Recipe(
            title=request.POST["title"],
            chef=request.POST["chef"],
            ingredients=request.POST["ingredients"],
            preparation=request.POST["preparation"],
            information=request.POST["information"],
            owner=user
        )
        recipe.save()

        files = request.FILES.getlist('photos')
        for file in files:
            new_file = File(
                file=file,
                name=file,
                path=f'/static/capstone/images/{file}'.replace(" ", "_"),
                recipe=recipe
            )
            new_file.save()
 
        return HttpResponseRedirect(reverse("myrecipe", args=(recipe.id,)))

    else:        
        return render(request, "capstone/admin/recipes/create.html")


@csrf_exempt
@login_required(redirect_field_name=None, login_url='/admin/login')
def edit_view(request, id):
    recipe = Recipe.objects.get(pk=id)
    files = File.objects.filter(recipe=id)
    user = User.objects.get(pk=request.user.id)
    
    if request.method == "POST":
        images = request.FILES.getlist('photos')
        if len(images) > 0:
            for file in files:
                File.objects.filter(pk=file.id).delete()
            
            for image in images:
                new_file = File(
                    file=image,
                    name=image,
                    path=f'/static/capstone/images/{image}'.replace(" ", "_"),
                    recipe=recipe
                )
                new_file.save()

        return HttpResponseRedirect(reverse("myrecipe", args=(recipe.id,)))

    if request.method == "PUT":
        # Ensure a user can't edit anyone's recipe 
        if user == recipe.owner:
            # Update post content into database
            data = json.loads(request.body)

            recipe.title = data["title"]
            recipe.chef = data["chef"]
            recipe.ingredients = data["ingredients"]
            recipe.preparation = data["preparation"]
            recipe.information = data["information"]

            recipe.save()

            return HttpResponse(status=204)

        else:
            return HttpResponseRedirect(reverse("myrecipes")) 

    else:        
        return render(request, "capstone/admin/recipes/edit.html", {
            'recipe': recipe,
            'files': files
        })


@csrf_exempt
@login_required(redirect_field_name=None, login_url='/admin/login')
def delete(request, id):
    recipe = Recipe.objects.get(pk=id)
    user = User.objects.get(pk=request.user.id)

    if request.method == "POST":
        # Ensure a user can't edit anyone's recipe 
        if user == recipe.owner:
            recipe.delete()

        return HttpResponseRedirect(reverse("myrecipes")) 


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            return HttpResponseRedirect(reverse("myrecipes"))

        else:
            return render(request, "capstone/admin/session/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "capstone/admin/session/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "capstone/admin/session/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "capstone/admin/session/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        return HttpResponseRedirect(reverse("myrecipes"))

    else:
        return render(request, "capstone/admin/session/register.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
