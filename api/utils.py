from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied

from main.models import SchedulePermission


def has_permission_to_schedule(user, level, schedule):
    if schedule.default_permission_level >= level:
        return True
    if user.is_anonymous:
        return False
    try:
        return SchedulePermission.objects.get(user=user, schedule=schedule).level >= level
    except ObjectDoesNotExist:
        return False


def check_permission_to_schedule(user, level, schedule):
    if not has_permission_to_schedule(user, level, schedule):
        raise PermissionDenied({"message": "You don't have permission to access",
                                "object_id": schedule.id})
