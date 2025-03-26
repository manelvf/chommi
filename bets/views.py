from django.shortcuts import render, redirect
from django.contrib.auth import logout


def index(request):
    return render(request, "bets/index.html")


def about(request):
    return render(request, "bets/about.html")


def service1(request):
    return render(request, "bets/service1.html")


def service2(request):
    return render(request, "bets/service2.html")


def all_services(request):
    return render(request, "bets/all_services.html")


def profile(request):
    return render(request, "bets/profile.html")


def logout(request):
    logout(request)

    redirect("home")
