from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("about", views.about, name="about"),
    path("create_event", views.create_event, name="create_event"),
    path("edit_event/<int:event_id>", views.edit_event, name="edit_event"),
    path("service2", views.service2, name="service2"),
    path("all_services", views.all_services, name="all_services"),
    path("profile", views.profile, name="profile"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("signup", views.signup, name="signup"),
]
