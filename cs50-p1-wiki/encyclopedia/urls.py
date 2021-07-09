from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("new-page", views.new_page, name="new_page"),
    path("wiki/<str:title>/edit", views.edit_page, name="edit_page"),
    path("random", views.get_random, name="random")
]
