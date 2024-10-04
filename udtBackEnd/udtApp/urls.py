from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("monitor", views.monitor, name="monitor"),
    path("entityList", views.entityList, name='entityList'),
    path("entityList/<str:entity_id>", views.entity, name='entity')
]