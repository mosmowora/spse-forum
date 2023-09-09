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
from .forms import RoomForm, UserCreationForm, UserForm
from online_users.models import OnlineUserActivity
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
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

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
            login(request, user)
            return redirect('home')
        else:
            errors = [error.errors for error in form if len(error.errors) > 0]
            messages.error(request, *errors)

    return render(request, 'base/login_register.html', {'form': form})


def home(request: HttpRequest):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).filter(
        Q(limited_for__in=(request.user.from_class.id,)) |
        Q(host=request.user)
    ) \
        .distinct() \
    \
    if not isinstance(request.user, AnonymousUser) else Room.objects.none()

    active_users = User.objects.filter(
        id__in=list(map(lambda u: u.user_id, OnlineUserActivity.get_user_activities(time_delta=timedelta(seconds=30))))
    )
    
    room_count = rooms.count()
    topics = Topic.objects.all()[:5]
    room_messages = sorted(Message.objects.filter(
        Q(room__topic__name__icontains=q)), key=lambda m: m.created, reverse=True)[:3]
    
    context = {'rooms': rooms, 'topics': topics, 'show_topics': sorted(topics[:4], key=lambda x: x.room_set.all().count(), reverse=True),
               'room_count': room_count, 'room_messages': room_messages, 'active_users': active_users}
    return render(request, 'base/home.html', context)


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

    for message in room_messages:
        upvoted = False
        if message.likes.filter(id=request.user.id).exists():
            upvoted = True

        upvoted_messages[message] = upvoted
        
    active_users = User.objects.filter(
        id__in=list(map(lambda u: u.user_id, OnlineUserActivity.get_user_activities(time_delta=timedelta(seconds=30))))
    )

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants, 'upvoted_messages': upvoted_messages, 'active_users': active_users}

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
            id__in=list(map(lambda u: u.user_id, OnlineUserActivity.get_user_activities(time_delta=timedelta(seconds=30))))
        )
        topics = Topic.objects.all()
        context = {'user': user, 'rooms': rooms,
                   'room_messages': room_messages, 'topics': topics, 'active_users': active_users}
        return render(request, 'base/profile.html', context)
    except Exception:
        return fallback(request)


def fallback(request: HttpRequest):
    return render(request, 'base/error-site.html')


@login_required(login_url='login', redirect_field_name=None)
def createRoom(request: HttpRequest):
    form = RoomForm(request.POST)
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        class_list = request.POST.getlist("limit_for")

        room = Room(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            pinned=True if request.POST.get('pinned') == "on" else False,
        )
        room.save()
        room.limited_for.set(set(int(x) for x in class_list))
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login', redirect_field_name=None)
def updateRoom(request: HttpRequest, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    form['limit_for'].initial = room.limited_for.get_queryset()

    if request.user != room.host and not request.user.is_superuser:
        return fallback(request)

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.pinned = True if request.POST.get('pinned') == "on" else False
        room.limited_for.set(request.POST.getlist("limit_for"))
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
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
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
