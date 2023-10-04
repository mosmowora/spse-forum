from django.contrib import admin
# Register your models here.

from .models import FromClass, Room, Topic, Message, User

class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'last_login', 'date_joined',
                       'password', 'name', 'username')


class AddStudentsToClassInline(admin.TabularInline):
    extra = 1
    model = User.from_class.through
    verbose_name = "Študent"
    verbose_name_plural = 'Študenti'
    
    class Media:
        css = {
            'all': ('..\\static\\styles\\admin.css', )     # Include extra css
        }

class ClassAdmin(admin.ModelAdmin):
    readonly_fields = ('set_class',)
    list_display = ['set_class']
    ordering = ('set_class',)
    inlines = [AddStudentsToClassInline]

admin.site.register(User, UserAdmin)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(FromClass, ClassAdmin)
