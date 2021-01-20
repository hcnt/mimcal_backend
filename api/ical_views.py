from datetime import datetime

from django_ical.feedgenerator import ICal20Feed
from django_ical.views import ICalFeed
from main.models import Event, Schedule


class EventFeed(ICalFeed):
    feed_type = ICal20Feed
    product_id = '-//Mimuw//Mimcal 21.3777//EN'
    timezone = 'Europe/Warsaw'
    file_name = "mimcal.ics"
    title = "Kalendarz"

    def file_name(self, obj):
        return "mimcal-%s-%s.ics" % obj.id, datetime.now()

    def get_object(self, request, schedule_id):
        return Schedule.objects.get(id=schedule_id)

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
