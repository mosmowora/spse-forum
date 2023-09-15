from typing import Self
from django.db import models
from django.contrib.auth.models import AbstractUser

class FromClass(models.Model):
    set_class = models.CharField(max_length=5)

    def __str__(self) -> str:
        return self.set_class


class User(AbstractUser):
    name = models.CharField(max_length=220, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, verbose_name='avatar')

    from_class = models.ForeignKey(
        FromClass, on_delete=models.SET_NULL, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.username



class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    pinned = models.BooleanField(null=False, default=False)
    limited_for = models.ManyToManyField(
        FromClass, related_name='room_limited_for')

    class Meta:
        ordering = ['-pinned', '-updated', '-created']

    def __str__(self): return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='messages')

    def total_upvotes(self):
        return self.likes.count()

    class Meta:
        ordering = ['updated', 'created']

    def __str__(self):
        return self.body[0:50]
