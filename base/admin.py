from collections import OrderedDict
from gettext import ngettext
from django.core.handlers.wsgi import WSGIRequest
from online_users.models import OnlineUserActivity
from typing import Any
from django.contrib import admin
from django.contrib import messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from base.forms import FromClassAdminForm, MessageForm, RoomAdminForm, TopicForm, UserAdminForm
import more_admin_filters as more_filters
from django.contrib.admin.actions import delete_selected
# Register your models here.

from .models import FromClass, Room, Topic, Message, User

class UserAdmin(admin.ModelAdmin):
    User.get_short_name = lambda user_instance: user_instance.name.split()[-1]
    
    readonly_fields = ('id', 'last_login', 'date_joined',
                       'name', 'username')
    list_filter = ['is_superuser', 'is_staff',
                   ('from_class',  more_filters.MultiSelectRelatedDropdownFilter)]
    exclude = ('first_name', 'last_name')
    fields = ['name', 'email', 'password', 'is_staff', 'groups',
              'bio', 'from_class', 'date_joined', 'last_login']
    list_display = ['name', 'email',  'bio',
                    'fromClass', 'date_Joined', 'last_Login']
    filter_horizontal = ['from_class',]
    search_fields = ['name']
    form = UserAdminForm
    
    delete_selected.short_description = u'Vymazať vybrané položky'

    def get_actions(self, request: HttpRequest) -> OrderedDict[Any, Any]:
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            del actions["delete_selected"]
        return actions

    @admin.action(description="Povýšiť na admina")
    def promote_to_admin(self, request, queryset: QuerySet[User]):
        updated = queryset.update(is_staff=True)
        self.message_user(
            request,
            ngettext(
                "%d užívateľ bol zmenený na admina",
                "%d užívatelia boli zmenení na admina",
                updated
            )
            % updated,
            messages.SUCCESS
        )
        

    @admin.action(description="Spraviť užívateľom")
    def demote_to_user(self, request, queryset: QuerySet[User]):
        updated = queryset.update(is_staff=False, is_superuser=False)
        self.message_user(
            request,
            ngettext(
                "%d užívateľ bol zmenený na užívateľa",
                "%d užívatelia boli zmenení na užívateľov",
                updated
            )
            % updated,
            messages.SUCCESS
        )

    actions = [promote_to_admin, demote_to_user]
    
    def date_Joined(self, obj: User):
        return obj.date_joined.strftime("%d %b %Y")

    def last_Login(self, obj: User):
        return obj.last_login.strftime("%d %b %Y %H:%M")


    class Media:
        js = ('..\\static\\js\\admin.js',)
        css = {
            'all': ('..\\static\\styles\\admin.css', )     # Include extra css
        }

    @admin.display(description=r"Trieda/Skupina")
    def fromClass(self, obj: User):
        return n if (n:=FromClass.objects.filter(id__in=obj.from_class.all())[0]) is not None else None

class AddStudentsToClassInline(admin.TabularInline):
    extra = 1
    # Display users that belong to this class
    model = User.from_class.through
    verbose_name = "Študent"
    verbose_name_plural = 'Študenti'
    
    class Media:
        css = {
            'all': ('..\\static\\styles\\admin.css', )     # Include extra css
        }

class RoomAdmin(admin.ModelAdmin):
    list_display = ['host', 'topic', 'name', 'description',
                    'participants', 'pinned', 'limited_for']
    fields = ['host', 'topic', 'name', 'description',
              'participants', 'pinned', 'limited_for']
    form = RoomAdminForm
    search_fields = ['host', 'topic', 'name', 'limited_for']
    
    @admin.display
    def participants(self, obj: Room):
        return obj.participants.all().count()

    @admin.display
    def limited_for(self, obj: Room):
        return obj.limited_for.all().count()
    
    class Media:
        js = ('..\\static\\js\\admin.js',)

class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']
    form = TopicForm
    search_fields = ['name']
    
    class Media:
        js = ('..\\static\\js\\admin.js',)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'body', 'likes_count', 'parent']
    fields = ['user', 'room', 'body', 'likes', 'parent']
    form = MessageForm
    search_fields = ['room__name', 'body']
    
    @admin.display(description='Počet palcov hore')
    def likes_count(self, obj: Message):
        return obj.likes.count()

    class Media:
        js = ('..\\static\\js\\admin.js',)

class ClassAdmin(admin.ModelAdmin):
    list_display = ['set_class']
    ordering = ('set_class',)
    inlines = [AddStudentsToClassInline]
    form = FromClassAdminForm
    search_fields = ['set_class']
    
    class Media:
        js = ('..\\static\\js\\admin.js',)

admin.site.register(User, UserAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(FromClass, ClassAdmin)
OnlineUserActivity._meta.verbose_name_plural = "Online užívatelia"
admin.site.site_title = "SPŠE Administrácia"
admin.site.site_header = "SPŠE Forum Administrácia"
admin.site.index_title = "SPŠE Forum Administrácia | Domov"