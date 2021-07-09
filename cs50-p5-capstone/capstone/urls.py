from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("recipes", views.recipes, name="recipes"),
    path("recipes/<int:id>", views.recipe, name="recipe"),
    path("filter", views.filter, name="filter"),
    path("admin/login", views.login_view, name="login"),
    path("admin/register", views.register, name="register"),
    path("admin/logout", views.logout_view, name="logout"),
    path("admin/myrecipes", views.myrecipes, name="myrecipes"),
    path("admin/myrecipes/<int:id>", views.myrecipe, name="myrecipe"),
    path("admin/myrecipes/create", views.create_view, name="create"),
    path("admin/myrecipes/<int:id>/edit", views.edit_view, name="edit"),
    path("admin/myrecipes/<int:id>/delete", views.delete, name="delete")
]
