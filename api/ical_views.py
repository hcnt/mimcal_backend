from django.core.exceptions import ObjectDoesNotExist
from django_ical.feedgenerator import ICal20Feed
from django_ical.views import ICalFeed
from main.models import Event, Schedule
from api.utils import has_permission_to_schedule

from django.contrib.auth.mixins import UserPassesTestMixin


class EventFeed(ICalFeed):
    feed_type = ICal20Feed
    product_id = '-//Mimuw//Mimcal 21.3777//EN'
    timezone = 'Europe/Warsaw'

    def file_name(self, obj):
        return "mimcal-%s.ics" % (obj.id)

    def title(self, obj):
        return obj.name

    def get_object(self, request, schedule_id):
        schedule = Schedule.objects.get(id=schedule_id)
        if not has_permission_to_schedule(request.user, 1, schedule):
            raise ObjectDoesNotExist
        return schedule

    def items(self, schedule: Schedule):
        return Event.objects.filter(schedule=schedule).order_by('-start_date')

    def item_title(self, event: Event):
        return event.title

    def item_description(self, event: Event):
        return event.desc

    def item_start_datetime(self, event: Event):
        return event.start_date

    def item_end_datetime(self, event: Event):
        return event.end_date

    def item_link(self, item):
        return ''

    def item_guid(self, item):
        return "mimcal:" + str(item.id)
