from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from main.models import Schedule, EventType, Event, User, SchedulePermission

from main.models import Comment, CommentReply


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    is_checked = serializers.SerializerMethodField('_is_checked')

    def _is_checked(self, obj):
        user_id = self.context.get("user_id", False)
        if user_id:
            return user_id in obj.users_marks.all()
        return False

    class Meta:
        model = Event
        exclude = ('users_marks',)


class ScheduleSerializer(serializers.ModelSerializer):
    my_permission_level = serializers.SerializerMethodField('_my_permission_level')

    def _my_permission_level(self, obj):
        user = self.context.get("user", False)
        if user and not user.is_anonymous:
            try:
                permission = SchedulePermission.objects.get(schedule=obj, user=user)
                return permission.level
            except ObjectDoesNotExist:
                return obj.default_permission_level
        return obj.default_permission_level

    class Meta:
        model = Schedule
        fields = ('id', 'name', 'owner_id', 'default_permission_level', 'my_permission_level')


class ScheduleWithEventsSerializer(ScheduleSerializer):
    events = serializers.ListField(read_only=True,
                                   child=EventSerializer(), source='event_set.all')
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta(ScheduleSerializer.Meta):
        fields = ('id', 'name', 'owner_id', 'events', 'default_permission_level', 'my_permission_level')


class BaseCommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    is_liked_by_me = serializers.SerializerMethodField('_is_liked_by_me')
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    def _is_liked_by_me(self, obj):
        user_id = self.context.get("user_id", False)
        if user_id:
            return user_id in obj.liked_users.all()
        return False


class CommentReplySerializer(BaseCommentSerializer):
    class Meta:
        model = CommentReply
        fields = ('id', 'content', 'likes_count', 'event', 'is_liked_by_me', 'author', 'reply_to')


class CommentSerializer(BaseCommentSerializer):
    replies = serializers.ListField(read_only=True, allow_empty=True,
                                    child=CommentReplySerializer(), source='commentreply_set.all')

    class Meta:
        model = Comment
        fields = ('id', 'content', 'replies', 'likes_count', 'event', 'is_liked_by_me', 'author')


class SchedulePermissionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = SchedulePermission
        fields = ('level', 'schedule', 'user')
