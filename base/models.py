from multiprocessing.managers import BaseManager
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

class FromClass(models.Model):
    set_class = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.set_class


class User(AbstractUser, PermissionsMixin):
    name = models.CharField(max_length=220, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, verbose_name='avatar')

    from_class = models.ManyToManyField(
        FromClass, related_name='from_class'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.name



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
    body = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='messages')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def total_upvotes(self):
        return self.likes.count()
    
    @property
    def children(self) -> BaseManager:
        return Message.objects.filter(parent=self)
    
    @children.setter
    def children(self, x: BaseManager) -> None:
        objs = Message.objects.filter(parent=self)
        objs = x
    
    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]
