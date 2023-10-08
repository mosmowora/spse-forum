from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import FromClass, Message, Room, Topic, User


class UserCreationForm(UserCreationForm):
    from_class = forms.ModelChoiceField(
        queryset=FromClass.objects.all(),
        widget=forms.Select
    )

    class Meta:
        model = User
        fields = ['name', 'username', 'email',
                  'from_class', 'password1', 'password2']

TOPIC_FIELDS_NAME = ['name']
TOPIC_FIELDS_LABEL = ["Téma"]
topic_label_list=dict(zip(TOPIC_FIELDS_NAME, TOPIC_FIELDS_LABEL))   
class TopicForm(ModelForm):
    class Meta:
        model=Topic
        fields='__all__'
        labels=topic_label_list
        
        
MESSAGE_FIELDS_NAME = ['user', 'room', 'body', 'likes', 'parent']
MESSAGE_FIELDS_LABEL = ['Napísal', "Názov diskusie", "Správa", "Počet likov", "Odpovedal na"]
message_label_list=dict(zip(MESSAGE_FIELDS_NAME, MESSAGE_FIELDS_LABEL))
class MessageForm(ModelForm):
    class Meta:
        model=Message
        fields='__all__'
        labels=message_label_list


ROOM_FIELDS_NAME = ['host', 'topic', 'name', 'description', 'participants', 'pinned', 'limited_for']
ROOM_FIELDS_LABEL = ['Autor', "Téma", "Názov", "Popis", "Zúčastnení", 'Pinnuté', 'Ukáže sa pre']
room_label_list=dict(zip(ROOM_FIELDS_NAME, ROOM_FIELDS_LABEL))
class RoomFormAdmin(ModelForm):
    class Meta:
        model=Room
        fields='__all__'
        labels=room_label_list


USER_FIELDS_NAME = ['name', 'email', 'bio', 'from_class', 'date_joined', 'last_login']
USER_FIELDS_LABEL = ['Meno', "E-mail", "O mne", "Trieda", 'Pridal sa', 'Naposledy na portáli']
user_label_list=dict(zip(USER_FIELDS_NAME, USER_FIELDS_LABEL))
class UserAdminForm(ModelForm):
    class Meta:
        model=User
        fields='__all__'
        labels=user_label_list
        
        

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
