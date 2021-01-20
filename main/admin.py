from django.contrib import admin
from main.models import Event, Schedule, EventType, Comment, CommentReply, User, SchedulePermission

admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(Comment)
admin.site.register(CommentReply)
admin.site.register(User)
admin.site.register(SchedulePermission)
admin.site.register(Schedule)
