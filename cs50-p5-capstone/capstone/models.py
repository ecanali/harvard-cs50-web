from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Recipe(models.Model):
    title = models.TextField(blank=True)
    chef = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    preparation = models.TextField(blank=True)
    information = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="recipes")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "chef": self.chef,
            "ingredients": self.ingredients,
            "preparation": self.preparation,
            "information": self.information,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "owner": self.owner
        }


class File(models.Model):
    name = models.TextField(blank=True)
    path = models.TextField(blank=True)
    file = models.FileField(upload_to='capstone/static/capstone/images/', null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="files")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "file": self.file,
            "recipe": self.recipe
        }
