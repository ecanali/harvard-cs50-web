from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes
        }


class Follower(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following")
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "follower": self.follower
        }


class Like(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="liker")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post")
    
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "post": self.post
        }
