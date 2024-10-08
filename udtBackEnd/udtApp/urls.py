from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index, name="index"),
    path("monitor", views.monitor, name="monitor"),
    path("entityList", views.entityList, name='entityList'),
    path("entityList/<str:entity_id>", views.entity, name='entity'),
    path("simulation", views.simulation, name='simulation'),
    path("simulation/<str:folder>/", views.serve_image, name='serve_image')
]