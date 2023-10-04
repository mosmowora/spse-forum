from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import FromClass, Message, Room, User


class UserCreationForm(UserCreationForm):
    from_class = forms.ModelChoiceField(
        queryset=FromClass.objects.all(),
        widget=forms.Select
    )

    class Meta:
        model = User
        fields = ['name', 'username', 'email',
                  'from_class', 'password1', 'password2']


class ReplyForm(ModelForm):

    class Meta:
        model = Message
        fields = ['body','parent']
        
        labels = {
            'body': (''),
        }
        
        widgets = {
            'body' : forms.TextInput(),
        }

    

class NewClassForm(ModelForm):

    set_class = forms.TextInput(attrs={"maxlength": 30})
    meno = forms.CharField(
        label='Meno',
        widget=forms.TextInput(),
        max_length=255,
        required=True
    )
    email = forms.CharField(
        label='Email',
        widget=forms.TextInput(),
        max_length=255,
        required=True
    )

    class Meta:
        model = FromClass
        fields = ['set_class']


class RoomForm(ModelForm):
    selection = forms.CheckboxSelectMultiple()

    limit_for = forms.ModelMultipleChoiceField(
        queryset=FromClass.objects.all(),
        widget=selection
    )

    class Meta:
        model = Room
        fields = ['topic', 'name', 'description', 'pinned', 'limit_for']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']


class ChangePasswordForm(UserCreationForm, ModelForm):

    class Meta:
        model = User
        fields = ['password1', 'password2']
