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
        if user_id and not isinstance(obj, dict):
            return user_id in obj.users_marks.all()
        return False

    class Meta:
        model = Event
        exclude = ('users_marks',)


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'name', 'owner_id', 'default_permission_level')


class ScheduleWithEventsSerializer(serializers.ModelSerializer):
    events = serializers.ListField(read_only=True,
                                   child=EventSerializer(), source='event_set.all')
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Schedule
        fields = ('id', 'name', 'owner_id', 'events', 'default_permission_level')


class CommentReplySerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CommentReply
        fields = ('content', 'likes_count', 'author_id', 'event', 'reply_to')


class CommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    replies = serializers.ListField(read_only=True, allow_empty=True,
                                    child=CommentReplySerializer(), source='comment_set.all')

    class Meta:
        model = Comment
        fields = ('content', 'replies', 'likes_count', 'author_id', 'event')


class SchedulePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulePermission
        fields = ('level', 'schedule')
