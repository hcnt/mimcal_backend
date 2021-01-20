from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_TEXT_FIELD_LENGTH = 4096

# "If you’re starting a new project,
# it’s highly recommended to set up a custom user model,
# even if the default User model is sufficient for you.
# This model behaves identically to the default user model,
# but you’ll be able to customize it in the future if the need arises"
# Source - django docs
class User(AbstractUser):
    pass


# Class = SQL table
# Field = SQL column
# Column with id is added automatically
class Schedule(models.Model):
    name = models.TextField(max_length=MAX_TEXT_FIELD_LENGTH)
    owner = models.ForeignKey(User, related_name='owned_schedules', on_delete=models.CASCADE)
    permitted_users = models.ManyToManyField(User, through='SchedulePermission')
    default_permission_level = models.IntegerField()


class SchedulePermissionLevels(models.IntegerChoices):
    RESTRICTED_ACCESS = 0, 'Restricted access'
    READ_ACCESS = 1, 'Read access'
    READ_WRITE_ACCESS = 2, 'Read and write access'
    MANAGE_ACCESS = 3, 'Manage access'


class SchedulePermission(models.Model):
    level = models.IntegerField(choices=SchedulePermissionLevels.choices)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class EventType(models.Model):
    name = models.TextField(max_length=MAX_TEXT_FIELD_LENGTH)


# ManyToManyField automatically creates new table
class Event(models.Model):
    title = models.TextField(max_length=MAX_TEXT_FIELD_LENGTH)
    desc = models.TextField(max_length=MAX_TEXT_FIELD_LENGTH, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    users_marks = models.ManyToManyField(User)
    type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-start_date']


class Comment(models.Model):
    content = models.TextField(max_length=MAX_TEXT_FIELD_LENGTH)
    likes_count = models.IntegerField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    liked_users = models.ManyToManyField(User, related_name='liked_comments')


class CommentReply(models.Model):
    content = models.TextField(max_length=MAX_TEXT_FIELD_LENGTH)
    likes_count = models.IntegerField()
    reply_to = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='reply_comments', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    liked_users = models.ManyToManyField(User, related_name='liked_reply_comments')
