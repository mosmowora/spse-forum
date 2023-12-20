from datetime import timedelta
import datetime
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse
from .models import (
    EmailPasswordVerification, Room, Topic, Message, User
)
from .forms import (
    ChangePasswordForm, NewClassForm,
    ReplyForm, RoomForm, UserCreationForm, UserForm
)
from online_users.models import OnlineUserActivity
from django.core.mail import send_mail
from urllib.parse import quote, unquote
# Create your views here.

ENCRYPTION_MAGIC = 12


def loginPage(request: HttpRequest):
    """
    Login page form
    """
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
    """
    Register page form
    """
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
    """
    Home page
    """
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    request.session.set_expiry(timedelta(hours=6))
    request.session.clear_expired()
    rooms = None
    
    if not isinstance(request.user, AnonymousUser):
        if request.user.is_staff:
            rooms = Room.objects.filter(
                (Q(topic__name__iexact=q) if q != '' else Q(topic__name__icontains=q)) |
                (Q(name__icontains=q))
            ).distinct()
        else:
            rooms = Room.objects.filter(
                (Q(topic__name__iexact=q) if q != '' else Q(topic__name__icontains=q)) |
                (Q(name__icontains=q))
            ).filter(
                Q(limited_for__in=request.user.from_class.all()) |
                Q(host=request.user)
            ).distinct()
    else:
        rooms = Room.objects.none()

    activities = OnlineUserActivity.get_user_activities(
        time_delta=timedelta(seconds=30))

    active_users = User.objects.filter(
        id__in=map(lambda u: u.user_id, activities)
    )

    room_count = rooms.count()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    if not isinstance(request.user, AnonymousUser):
        room_messages = sorted(room_messages.filter(
            Q(room__limited_for__in=request.user.from_class.all())
        ), key=lambda x: x.created, reverse=True)

    elif isinstance(request.user, AnonymousUser):
        for message in room_messages:
            message.body = '????'
            message.room.name = 'neznáme'

    context = {'rooms': rooms, 'topics': tuple(filter(lambda x: x.room_set.all().count() != 0, topics)), 'show_topics': tuple(filter(lambda y: y.room_set.all().count() != 0, sorted(topics, key=lambda x: x.room_set.all().count(), reverse=True)))[:4],
               'room_count': room_count, 'room_messages': room_messages[:3], 'active_users': active_users}
    return render(request, 'base/home.html', context)


def newClass(request: HttpRequest):
    """
    Form for creating a new class or group
    """
    form = NewClassForm()

    if request.method == 'POST':
        send_mail(
            subject='SPŠE Forum žiadosť',
            message=f'{request.POST.get("meno")} požiadal o vytvorenie skupiny s menom {request.POST.get("set_class")}',
            from_email='tomas.nosal04@gmail.com',
            # TODO: email from request ↓
            recipient_list=['reknojorke@gufum.com',],
            fail_silently=False
        )

    return render(request, 'base/new_class_entry.html', {'form': form})


def pinRoom(request: HttpRequest, pk):
    """
    Logic for pinning or unpinning a room
    """

    pinned_room: Room = Room.objects.get(id=pk)
    pinned_room.pinned = not pinned_room.pinned
    pinned_room.save()
    return HttpResponseRedirect(reverse('home'))


@login_required(login_url='login', redirect_field_name=None)
def room(request: HttpRequest, pk):
    """
    Page for showing everything about the room, handling room messages, message upvotes, participants, etc.
    """
    try:
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
        context = {'room': room, 'room_messages': room_messages, 'amount_of_messages': len(room_messages),
                   'participants': participants, 'upvoted_messages': upvoted_messages, 'active_users': active_users, 'back': any(x in ('room', 'error', 'delete-message', 'upvote-message') for x in back.split("/"))}
        if request.method == 'POST':
            content = request.POST.get('body')
            parent = None
            reply_form = ReplyForm(data=request.POST)

            if reply_form.is_valid():
                content = reply_form.cleaned_data['body']
                try:
                    parent = reply_form.cleaned_data['parent']
                except Exception:
                    parent = None

            if content == '':
                return redirect('room', pk=room.id)

            try:
                parent = Message.objects.get(id=reply_form['parent'].value())
            except Exception:
                parent = None

            message = Message(
                user=request.user,
                room=room,
                body=content,
                parent=parent
            )
            message.save()
            room.participants.add(request.user)
            return redirect('room', pk=room.id)
    except Exception:
        return fallback(request, "Nemožno zobraziť túto diskusiu.")

    return render(request, 'base/room.html', context)


def upvoteMessage(request: HttpRequest, pk):
    """
    Logic for upvoting or downvoting a message
    """
    message = Message.objects.get(id=request.POST.get('message_id'))

    if message.likes.filter(id=request.user.id).exists():
        message.likes.remove(request.user)
    else:
        message.likes.add(request.user)

    message.save()
    return HttpResponseRedirect(reverse('room', args=[message.room_id]))


def userProfile(request: HttpRequest, pk):
    """
    User's profile page
    """
    user = None
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
        if user is None:
            return fallback(request, message="Nenašiel som užívateľa")
        else:
            # This shouldn't happen
            return fallback(request, message="Tu nemáš čo hľadať")


def mailResponse(request: HttpRequest, pk, password: int):
    """
    E-mail confirmation handler\n
    get's the user based on his id and after decrypting the password from the url sets his new password.\n
    Handles password confirmation token expiry. Token expires after 1H.

    Params
    -----

    pk `str` - user's id\n
    password `str` - encrypted password taken from the url for decryption
    """

    user = User.objects.get(id=pk)
    expires = EmailPasswordVerification.objects.get(
        user__id=user.id).token_created + datetime.timedelta(hours=2)

    expires = expires.replace(tzinfo=datetime.datetime.now(
        datetime.timezone.utc).astimezone().tzinfo)
    now = datetime.datetime.now(tz=datetime.datetime.now(
        datetime.timezone.utc).astimezone().tzinfo)

    # Debugging purposes
    # print(expires)
    # print(now)

    if now > expires:
        return fallback(request, message="Token pre zmenu hesla vypršal.")

    user.set_password(decrypt(password))
    user.save()
    login(request, user)
    messages.success(request, 'Úspešne zmenené heslo')
    return redirect('home')


def encrypt(password: str) -> str:
    """
    Encryption logic for encrypting the user's new password into the confirmation URL

    Params
    ------
    password `str` - raw password to encrypt
    """
    return "".join(map(lambda s: chr(ord(s) + ENCRYPTION_MAGIC), password))


def decrypt(password: str) -> str:
    """
    Decryption logic for decrypting the user's new password from the confirmation URL

    Params
    ------
    password `str` - raw password to decrypt
    """
    password = unquote(password)
    new_pass = "".join(map(lambda s: chr(ord(s) - ENCRYPTION_MAGIC), password))
    return new_pass


def changePassword(request: HttpRequest):
    """
    If the user wants to change his password, handle it with this logic
    """
    user = None
    form = None
    try:
        user = User.objects.get(id=request.user.id)
        form = ChangePasswordForm(instance=user)
    except Exception:
        user = AnonymousUser()
        form = ChangePasswordForm(email=True)

    if request.method == 'POST':
        if request.POST.get('password1') == request.POST.get('password2'):
            if isinstance(user, AnonymousUser):
                student = User.objects.get(email=request.POST.get("email"))
                password = f'http://localhost:8000/email-response/{student.pk}/{quote(quote(encrypt(request.POST.get("password1")), encoding="utf-8"), safe=":/")}'
                htmly = get_template('base/email_template.html')
                html_content = htmly.render(
                    {'student': student, 'password': password})
                msg = EmailMultiAlternatives(
                    "SPŠE Forum zabudnuté heslo", "SPŠE Forum zabudnuté heslo", "tomas.nosal04@gmail.com", (request.POST.get("email"),))
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                messages.info(request, "Bol ti zaslaný potvrdzovací email")
                try:
                    got_user = EmailPasswordVerification.objects.get(
                        user=student)  # This is neccessary !!!
                    got_user.token_created = datetime.datetime.now() + datetime.timedelta(hours=1)
                    got_user.save()
                except Exception:
                    created = EmailPasswordVerification.objects.create(
                        user=student,
                        token_created=datetime.datetime.now() + datetime.timedelta(hours=1)
                    )
                    print(created)
                return render(request, 'base/home.html')

            else:
                if user.check_password(request.POST.get('password1')):
                    messages.error(
                        request, "Nemôžeš mať rovnaké heslo ako predtým")

                else:
                    user.set_password(request.POST.get('password1'))
                    user.save()
                    login(request, user)
                    messages.success(request, 'Úspešne si si zmenil heslo')
                    return redirect('user-profile', pk=user.id)
        else:
            messages.error(request, "Heslá nie sú rovnaké")

    return render(request, 'base/change_password.html', {'form': form})


def fallback(request: HttpRequest, message: str = None):
    """
    Error handler site (404 page)

    Params:
    ------
    message - `str`: optional message to display on the 404 page
    """
    return render(request, 'base/error-site.html', {'message': message})


@login_required(login_url='login', redirect_field_name=None)
def createRoom(request: HttpRequest):
    """
    Site for room creation, basically the form backend
    """
    try:
        if request.user.room_set.all().count() >= 10:
            messages.error(
                request, 'Dosiahol si maximálny počet vytvorených diskusií')
            return redirect('home')

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

            room.save()
            room.limited_for.set(selected_classes)
            return redirect('home')
    except Exception:
        return fallback(request, "Niečo sa stalo pri vytváraní diskusie.")

    return render(request, 'base/room_form.html', context)


@login_required(login_url='login', redirect_field_name=None)
def updateRoom(request: HttpRequest, pk):
    """
    Site for room updates, basically the form backend
    """
    try:
        room = Room.objects.get(id=pk)
        form = RoomForm(instance=room)
        topics = Topic.objects.all()
        form['limit_for'].initial = room.limited_for.get_queryset()
        context = {'form': form, 'topics': topics, 'room': room, 'back': any(
            x == 'update-room' for x in request.META['HTTP_REFERER'].split("/"))}

        if request.user != room.host and not request.user.is_staff:
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

    except Exception:
        return fallback(request)

    return render(request, 'base/room_form.html', context)


@login_required(login_url='login', redirect_field_name=None)
def deleteRoom(request: HttpRequest, pk):
    """
    Site for room deletion
    """
    room = Room.objects.get(id=pk)

    if request.user != room.host and not request.user.is_staff:
        return fallback(request)

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room, 'back': any(x == 'delete-room' for x in request.META['HTTP_REFERER'].split("/"))})


@login_required(login_url='login')
def deleteMessage(request, pk):
    """
    Site for room's message deletion
    """
    message = None
    try:
        message = Message.objects.get(id=pk)
    except Exception:
        messages.error(request, 'Správa neexistuje')
        return redirect('home')

    if request.user != message.user:
        return fallback(request, "Takto odstránenie správy nefunguje.")

    if request.method == 'POST':
        message.delete()
        # redirect user back to the room
        return redirect('room', pk=message.room.id)

    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login', redirect_field_name=None)
def updateUser(request: HttpRequest):
    """
    Site for updating the user's info
    """
    user = request.user
    form = UserForm(instance=user)

    try:
        if request.method == 'POST':
            form = UserForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect('user-profile', pk=user.id)
    except Exception:
        return fallback(request, "Niečo neočakávané sa stalo.")

    return render(request, 'base/update-user.html', {'form': form})


@login_required(login_url='login', redirect_field_name=None)
def deleteUser(request: HttpRequest):
    """
    Site for deleting everything about the user
    """
    try:
        if request.method == 'POST':
            messages = Message.objects.filter(
                user__email__exact=request.user.email)
            messages.delete()
            rooms = list(filter(lambda r: request.user in r.all(), [
                r.participants for r in Room.objects.all()]))
            for participants in rooms:
                participants.get(email__exact=request.user.email).delete()

            hosted_rooms = Room.objects.filter(
                host__name__exact=request.user.name)
            hosted_rooms.delete()
            user = User.objects.get(email__exact=request.user.email)
            user.delete()
    except Exception:
        return fallback(request, "Niečo sa stalo pri odstraňovaní tvojho účtu.")

    return render(request, 'base/delete-user.html')


def topicsPage(request: HttpRequest):
    """
    Site for showing topics
    """
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    render_value = ""
    type_of = "topic"

    try:
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
    except Exception:
        return fallback(request)

    return render(request, 'base/topics.html', {'topics': tuple(filter(lambda x: x.room_set.all().count() != 0, topics)), 'render_value': render_value, "type_of": type_of})


def activityPage(request):
    """
    Activity page with room messages
    """
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})
