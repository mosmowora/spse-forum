from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['topic', 'name', 'description', 'is_private', 'pinned']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
