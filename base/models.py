from multiprocessing.managers import BaseManager
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.forms import ValidationError


class FromClass(models.Model):
    set_class = models.CharField(max_length=30)
    custom = models.BooleanField(default=False, null=False)

    def __str__(self) -> str:
        return self.set_class
    
    class Meta:
        verbose_name = r"Triedu/skupinu"
        verbose_name_plural = "Triedy a skupiny"

class EmailPasswordVerification(models.Model):
    user = models.ForeignKey('base.User', on_delete=models.CASCADE)
    token_created = models.DateTimeField(auto_now_add=True)


def validate_image(image):
    file_size = image.file.size
    limit_mb = 4

    if file_size > limit_mb * 1024 * 1024:
       raise ValidationError(f"Najväčšia veľkosť súboru je {limit_mb} MB")

class User(AbstractUser, PermissionsMixin):
    name = models.CharField(max_length=220, null=True, db_column="Meno")
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, verbose_name='avatar', validators=[validate_image])
    school_year = models.CharField(max_length=50, null=True)
    registered_groups = models.ManyToManyField(FromClass, related_name="registered_groups")

    from_class = models.ManyToManyField(
        FromClass, related_name='from_class'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email
    
    @property
    def users_name(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Užívateľ"
        verbose_name_plural = "Užívatelia"


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    
    class Meta:
        verbose_name = "Téma diskusie"
        verbose_name_plural = "Témy diskusií"


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    subscribing = models.ManyToManyField(User, related_name="subscribing_rooms")
    file = models.ImageField(null=True, blank=True, verbose_name='room_image', max_length=512, upload_to="images/")

    pinned = models.BooleanField(null=False, default=False)
    limited_for = models.ManyToManyField(
        FromClass, related_name='room_limited_for')

    class Meta:
        ordering = ['-pinned', '-updated', '-created']
        verbose_name = "Diskusia"
        verbose_name_plural = "Diskusie"

    def __str__(self): return self.name

    @property
    def messages(self):
        return [
            {
                "id": m.id, 
                "author": m.user.id, 
                "body": m.body,
                "created_at": m.created, 
                "total_likes": m.total_upvotes(), 
                "parent": None if m.parent is None else m.parent.id
            }
            for m in self.message_set.all()
        ]


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='messages')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def total_upvotes(self):
        return self.likes.count()

    @property
    def children(self) -> BaseManager:
        return Message.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

    class Meta:
        ordering = ['-created']
        verbose_name = "Správa diskusie"
        verbose_name_plural = "Správy diskusií"

    def __str__(self):
        return self.body[0:50]
