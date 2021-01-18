from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Exists, OuterRef
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework import permissions, mixins
from rest_framework import viewsets
from rest_framework.viewsets import GenericViewSet

from api.serializers import ScheduleSerializer, EventSerializer, ScheduleWithEventsSerializer
from main.models import Schedule, Event, EventType, SchedulePermission, SchedulePermissionLevels
from main.models import SchedulePermissionLevels as Level

from api.serializers import CommentSerializer, CommentReplySerializer
from main.models import Comment, CommentReply
from rest_registration.signals import user_changed_email


def has_perm_to_schedule(user, level, schedule):
    if schedule.default_permission_level >= level:
        return True
    if user.is_anonymous:
        return False
    try:
        return SchedulePermission.objects.get(user=user, schedule=schedule).level >= level
    except ObjectDoesNotExist:
        return False


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.method in SAFE_METHODS:
            needed_level = SchedulePermissionLevels.READ_ACCESS
        elif self.action in ['add_permitted_user', 'remove_permitted_user']:
            needed_level = SchedulePermissionLevels.MANAGE_ACCESS
        else:
            needed_level = SchedulePermissionLevels.READ_WRITE_ACCESS
        if self.request.user.is_anonymous:
            return Schedule.objects.filter(default_permission_level__gte=needed_level)
        return Schedule.objects.filter(
            Q(default_permission_level__gte=needed_level) |
            Q(Exists(SchedulePermission.objects
                     .filter(schedule=OuterRef('id'),
                             user=self.request.user,
                             level__gte=needed_level))
              ))

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'create':
            return ScheduleSerializer
        return ScheduleWithEventsSerializer

    def perform_create(self, serializer):
        obj = serializer.save(owner=self.request.user)
        obj.permitted_users.add(self.request.user, through_defaults={'level': Level.MANAGE_ACCESS})

    @action(detail=True, methods=['GET'])
    def events(self, request, pk=None):
        schedule = self.get_object()

        if not has_perm_to_schedule(self.request.user, 0, schedule):
            raise PermissionDenied({"message": "You don't have permission to access",
                                    "object_id": schedule.id})
        events = Event.objects.filter(schedule=schedule)
        n = self.request.query_params.get('n', None)
        if n:
            events = events[:int(n)]

        serializer = EventSerializer(events, many=True, context={'user_id': request.user})
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def change_user_perm(self, request, pk=None):
        schedule = self.get_object()
        try:
            level = int(self.request.query_params.get('level', None))
        except Exception:
            raise ValidationError
        username = self.request.query_params.get('username', None)
        if not level or not username:
            raise ValidationError
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ValidationError
        try:
            perm = SchedulePermission.objects.get(user=user, schedule=schedule)
            perm.level = level
        except ObjectDoesNotExist:
            SchedulePermission.objects.create(user=user, schedule=schedule, level=level)
            schedule.permitted_users.add(user)
        return Response({'status': 'changed permission level'})


class EventViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        context = super(EventViewSet, self).get_serializer_context()
        context.update({"user_id": self.request.user})
        return context

    @action(detail=True, methods=['post'])
    def check(self, request, pk=None):
        event = self.get_object()
        event.users_marks.add(request.user)
        return Response({'status': 'event checked'})

    @action(detail=True, methods=['post'])
    def uncheck(self, request, pk=None):
        event = self.get_object()
        event.users_marks.remove(request.user)
        return Response({'status': 'event unchecked'})

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        event = self.get_object()
        comments = Comment.objects.filter(event=event)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.liked_users.add(request.user)
        comment.likes_count += 1
        return Response({'status': 'comment liked'})

    @action(detail=True, methods=['post'])
    def unlike_reply(self, request, pk=None):
        comment = self.get_object()
        comment.liked_users.remove(request.user)
        comment.likes_count -= 1
        return Response({'status': 'comment unliked'})


class CommentReplyViewSet(mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    queryset = CommentReply.objects.all()
    serializer_class = CommentReplySerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        obj = serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.liked_users.add(request.user)
        comment.likes_count += 1
        return Response({'status': 'reply liked'})

    @action(detail=True, methods=['post'])
    def unlike_reply(self, request, pk=None):
        comment = self.get_object()
        comment.liked_users.remove(request.user)
        comment.likes_count -= 1
        return Response({'status': 'reply unliked'})
