from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("create_event/", views.create_event, name="create_event"),
    path("edit_event/<int:event_id>", views.edit_event, name="edit_event"),
    path("latest_events/", views.latest_events, name="latest_events"),
    path("popular_events/", views.popular_events, name="popular_events"),
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
    path("place_bet/<int:event_id>/", views.place_bet, name="place_bet"),
    path("my_bets/", views.my_bets, name="my_bets"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("contact/", views.contact, name="contact"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page='home'), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/profile/", views.profile, name="profile"),
]
