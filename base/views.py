from datetime import timedelta
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import Room, Topic, Message, User
from .forms import ChangePasswordForm, NewClassForm, RoomForm, UserCreationForm, UserForm
from online_users.models import OnlineUserActivity
from django.core.mail import send_mail
# Create your views here.


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except Exception:
            messages.error(request, 'Užívateľ neexistuje')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Zlý email alebo heslo')

    return render(request, 'base/login_register.html', {'page': page})


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request: HttpRequest):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.replace(" ", "_").lower()
            user.save()
            print('from_class', user.from_class)
            user.from_class.add(form.cleaned_data['from_class'])
            login(request, user)
            return redirect('home')
        else:
            errors = [error.errors for error in form if len(error.errors) > 0]
            messages.error(request, *errors)

    return render(request, 'base/login_register.html', {'form': form})


def home(request: HttpRequest):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = None
    if not isinstance(request.user, AnonymousUser):
        if request.user.is_superuser:
            rooms = Room.objects.filter(
                (Q(topic__name__iexact=q) if q != '' else Q(topic__name__icontains=q)) |
                (Q(name__icontains=q) |
                 Q(description__contains=q))
            ).distinct()
        else:
            rooms = Room.objects.filter(
                (Q(topic__name__iexact=q) if q != '' else Q(topic__name__icontains=q)) |
                (Q(name__icontains=q) |
                 Q(description__contains=q))
            ).filter(
                Q(limited_for__in=request.user.from_class.all()) |
                Q(host=request.user)
            ).distinct()
    else:
        rooms = Room.objects.none()

    active_users = User.objects.filter(
        id__in=list(map(lambda u: u.user_id, OnlineUserActivity.get_user_activities(
            time_delta=timedelta(seconds=30))))
    )

    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = sorted(Message.objects.filter(
        Q(room__topic__name__icontains=q)), key=lambda m: m.created, reverse=True)[:3]
        
    context = {'rooms': rooms, 'topics': topics, 'show_topics': sorted(topics[:4], key=lambda x: x.room_set.all().count(), reverse=True),
               'room_count': room_count, 'room_messages': room_messages, 'active_users': active_users}
    return render(request, 'base/home.html', context)


def newClass(request: HttpRequest):
    form = NewClassForm()

    if request.method == 'POST':

        send_mail(
            subject='SPŠE Forum žiadosť',
            message=f'{request.POST.get("meno")} požiadal o vytvorenie skupiny s menom {request.POST.get("set_class")}',
            from_email='tomas.nosal04@gmail.com',
            recipient_list=['reknojorke@gufum.com',],
            fail_silently=False
        )

    return render(request, 'base/new_class_entry.html', {'form': form})


def pinRoom(request: HttpRequest, pk):
    pinned_room: Room = Room.objects.get(id=pk)
    pinned_room.pinned = not pinned_room.pinned
    pinned_room.save()
    return HttpResponseRedirect(reverse('home'))


@login_required(login_url='login', redirect_field_name=None)
def room(request: HttpRequest, pk):
    room = Room.objects.get(id=pk)
    room_messages: QuerySet[Message] = room.message_set.all()
    room_messages = sorted(
        room_messages, key=lambda mess: mess.likes.count(), reverse=True)
    participants = room.participants.all()

    upvoted_messages: dict[Message, bool] = {}

    back: str = request.META['HTTP_REFERER']

    for message in room_messages:
        upvoted = False
        if message.likes.filter(id=request.user.id).exists():
            upvoted = True

        upvoted_messages[message] = upvoted

    active_users = User.objects.filter(
        id__in=list(map(lambda u: u.user_id, OnlineUserActivity.get_user_activities(
            time_delta=timedelta(seconds=30))))
    )

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants, 'upvoted_messages': upvoted_messages, 'active_users': active_users, 'back': any(x in ('room', 'error') for x in back.split("/"))}

    if request.method == 'POST':
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    return render(request, 'base/room.html', context)


def upvoteMessage(request: HttpRequest, pk):
    message = Message.objects.get(id=request.POST.get('message_id'))

    if message.likes.filter(id=request.user.id).exists():
        message.likes.remove(request.user)
    else:
        message.likes.add(request.user)

    message.save()
    return HttpResponseRedirect(reverse('room', args=[message.room_id]))


def userProfile(request: HttpRequest, pk):
    try:
        user = User.objects.get(id=pk)
        rooms = user.room_set.all()
        room_messages = user.message_set.all()
        active_users = User.objects.filter(
            id__in=list(map(lambda u: u.user_id, OnlineUserActivity.get_user_activities(
                time_delta=timedelta(seconds=30))))
        )
        topics = Topic.objects.all()
        context = {
            'user': user, 'rooms': rooms, 'from_class': user.from_class.filter(set_class__startswith="I")[0],
            'room_messages': room_messages, 'topics': topics,
            'show_topics': sorted(topics[:4], key=lambda x: x.room_set.all().count(), reverse=True), 'active_users': active_users
        }
        return render(request, 'base/profile.html', context)
    except Exception:
        return fallback(request)


@login_required(login_url='login', redirect_field_name=None)
def changePassword(request: HttpRequest):
    user = User.objects.get(id=request.user.id)
    form = ChangePasswordForm(instance=user)
    
    if request.method == 'POST':
        if request.POST.get('password1') == request.POST.get('password2'):
            if user.check_password(request.POST.get('password1')): messages.error(request, "Nemôžeš mať rovnaké heslo ako predtým")
            
            else:
                user.set_password(request.POST.get('password1'))
                user.save()
                login(request, user)
                messages.success(request, 'Úspešne si si zmenil heslo')
                return redirect('user-profile', pk=user.id)
        else:
            messages.error(request, "Heslá nie sú rovnaké")
        
    return render(request, 'base/change_password.html', {'form': form})


def fallback(request: HttpRequest):
    return render(request, 'base/error-site.html')


@login_required(login_url='login', redirect_field_name=None)
def createRoom(request: HttpRequest):
    form = RoomForm(request.POST)
    topics = Topic.objects.all()
    context = {'form': form, 'topics': topics}

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        class_list = request.POST.getlist("limit_for")
        context['back'] = any(
            x == 'create-room' for x in request.META['HTTP_REFERER'].split("/"))

        room = Room(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            pinned=True if request.POST.get('pinned') == "on" else False
        )

        selected_classes = set(int(x) for x in class_list)
        if len(selected_classes) == 0:
            context['message'] = 'Musíš zaškrtnúť pre koho sa ukáže'
            return render(request, 'base/room_form.html', context)

        if request.user.room_set.all().count() >= 3:
            messages.error(request, 'Dosiahol si maximálny počet vytvorených diskusií')
            return redirect('home')
        room.save()
        room.limited_for.set(selected_classes)
        return redirect('home')

    return render(request, 'base/room_form.html', context)


@login_required(login_url='login', redirect_field_name=None)
def updateRoom(request: HttpRequest, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    form['limit_for'].initial = room.limited_for.get_queryset()
    context = {'form': form, 'topics': topics, 'room': room, 'back': any(
        x == 'update-room' for x in request.META['HTTP_REFERER'].split("/"))}

    if request.user != room.host and not request.user.is_superuser:
        return fallback(request)

    if request.method == 'POST':
        class_list = request.POST.getlist("limit_for")
        topic_name = request.POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.pinned = True if request.POST.get('pinned') == "on" else False
        room.limited_for.set(request.POST.getlist("limit_for"))
        selected_classes = set(int(x) for x in class_list)
        if len(selected_classes) == 0:
            context['message'] = 'Musíš zaškrtnúť pre koho sa ukáže'
            return render(request, 'base/room_form.html', context)

        room.save()
        return redirect('home')

    return render(request, 'base/room_form.html', context)


@login_required(login_url='login', redirect_field_name=None)
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host and not request.user.is_superuser:
        return fallback(request)

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return fallback(request)

    if request.method == 'POST':
        message.delete()
        # redirect user back to the room
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login', redirect_field_name=None)
def updateUser(request: HttpRequest):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


@login_required(login_url='login', redirect_field_name=None)
def deleteUser(request: HttpRequest):
    if request.method == 'POST':
        messages = Message.objects.filter(user__name__exact=request.user.name)
        messages.delete()
        rooms = list(filter(lambda r: request.user in r.all(), [r.participants for r in Room.objects.all()]))
        for participants in rooms: participants.get(name__exact=request.user.name)
        
        hosted_rooms = Room.objects.filter(host__name__exact=request.user.name)
        hosted_rooms.delete()
        user = User.objects.get(name__exact=request.user.name)
        user.delete()
    
    return render(request, 'base/delete-user.html')

def topicsPage(request: HttpRequest):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    render_value = ""
    type_of = "topic"

    if request.method == "GET":
        if request.GET.get("search_for_students") is None:
            render_value = request.GET.get("search_for_topics")
            type_of = 'topic'
        else:
            render_value = request.GET.get("search_for_students")
            type_of = 'user'

    alphabet = {c: i for i, c in enumerate(
        'AÁÄBCČDĎDZDŽEÉFGHCHIÍJKLĹĽMNŇOÓÔPQRŔSŠTŤUÚVWXYÝZŽ')}
    topics = sorted(Topic.objects.filter(
        Q(name__icontains=q)), key=lambda x: x.room_set.all().count(), reverse=True) if type_of == "topic" \
        else sorted(User.objects.filter(Q(name__icontains=q) | Q(from_class__set_class__icontains=q)), key=lambda user: [alphabet.get(c, ord(c)) for c in user.name.split()[0]])

    return render(request, 'base/topics.html', {'topics': topics, 'render_value': render_value, "type_of": type_of})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
