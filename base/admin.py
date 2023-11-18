from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db.models import Count

from base.forms import MessageForm, RoomFormAdmin, TopicForm, UserAdminForm, UserForm
# Register your models here.

from .models import FromClass, Room, Topic, Message, User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'last_login', 'date_joined',
                       'name', 'username')
    exclude = ('first_name', 'last_name')
    fields = ['name', 'email', 'password', 'groups',
              'bio', 'from_class', 'date_joined', 'last_login']
    list_display = ['name', 'email',  'bio',
                    'fromClass', 'date_Joined', 'last_Login']
    filter_horizontal = ['from_class',]
    form = UserAdminForm

    def date_Joined(self, obj: User):
        return obj.date_joined.strftime("%d %b %Y")

    def last_Login(self, obj: User):
        return obj.last_login.strftime("%d %b %Y %H:%M")
    
    class Media:
        css = {
            'all': ('..\\static\\styles\\admin.css', )     # Include extra css
        }

    @admin.display(description="Trieda")
    def fromClass(self, obj: User):
        return FromClass.objects.filter(id__in=obj.from_class.all())[0]


class AddStudentsToClassInline(admin.TabularInline):
    extra = 1
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
    form = RoomFormAdmin

    @admin.display
    def participants(self, obj: Room):
        return obj.participants.all().count()

    @admin.display
    def limited_for(self, obj: Room):
        return obj.limited_for.all().count()


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']
    fields = ['name']
    form = TopicForm


class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'body', 'likes_count', 'parent']
    fields = ['user', 'room', 'body', 'likes', 'parent']
    form = MessageForm

    @admin.display(description='Počet palcov hore')
    def likes_count(self, obj: Message):
        return obj.likes.all().count()


class ClassAdmin(admin.ModelAdmin):
    list_display = ['set_class']
    ordering = ('set_class',)
    inlines = [AddStudentsToClassInline]


admin.site.register(User, UserAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(FromClass, ClassAdmin)
