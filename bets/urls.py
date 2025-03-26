from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about", views.about, name="about"),
    path("service1", views.service1, name="service1"),
    path("service2", views.service2, name="service2"),
    path("all_services", views.all_services, name="all_services"),
    path("profile", views.profile, name="profile"),
    path("logout", views.logout, name="logout"),
]
