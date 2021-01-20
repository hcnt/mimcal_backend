from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
import api.views as views
from api.ical_views import EventFeed

router = DefaultRouter()
router.register('schedules', views.ScheduleViewSet)
router.register('events', views.EventViewSet)
router.register('comments', views.CommentViewSet)
router.register('commentReplies', views.CommentReplyViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('schedules/<int:schedule_id>/to_webcal/', EventFeed()),
    path('', include(router.urls)),
    path('auth/', include('rest_registration.api.urls')),
]
