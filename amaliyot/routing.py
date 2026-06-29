from django.urls import re_path
from .consumers import OlympiadProgressConsumer

websocket_urlpatterns = [
    re_path(r"ws/olympiad/(?P<group_id>\d+)/$", OlympiadProgressConsumer.as_asgi()),
]










