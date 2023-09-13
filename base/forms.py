from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import FromClass, Room, User


class UserCreationForm(UserCreationForm):
    from_class = forms.ModelChoiceField(
        queryset=FromClass.objects.all(),
        widget=forms.Select
    )

    class Meta:
        model = User
        fields = ['name', 'username', 'email',
                  'from_class', 'password1', 'password2']

class RoomForm(ModelForm):
    selection = forms.CheckboxSelectMultiple()
    
    limit_for = forms.ModelMultipleChoiceField(
        queryset=FromClass.objects.all(),
        widget=selection
    )
    
    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        print("error", self.fields['limit_for'].error_messages)
        self.fields['limit_for'].error_messages = {'required': 'Zaškrtni aspoň jednu triedu, ktorej sa to zobrazí'}
    class Meta:
        model = Room
        fields = ['topic', 'name', 'description', 'pinned', 'limit_for']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
