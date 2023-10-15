from rest_framework import serializers
from base.models import Room, User


class RoomSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    
    def get_messages(self, obj):
        return Room.objects.get(id=obj.id).messages
    class Meta:
        model = Room
        fields = ('id', 'host', 'topic', 'name', 'description', 'participants', 'updated', 'created', 'pinned', 'limited_for', 'messages')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'last_login', 'is_superuser', 'is_active', 'date_joined', 'from_class', 'bio')