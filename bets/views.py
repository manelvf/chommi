from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf.urls.static import static

from .forms import ImageUploadForm, EventOptionFormSet


def index(request):
    gallery_images = [
        {
            "url": static("images/image1.jpg"),
            "alt": "First Image",
            "title": "Amazing Landscape with Mountains and a River",
            "description": "A beautiful scene from our collection",
        },
        # Add more images...
    ]

    return render(request, "bets/home.html", {"gallery_images": gallery_images})


def about(request):
    return render(request, "bets/about.html")


def create_event(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES, label_suffix="")
        formset = EventOptionFormSet(request.POST, instance=form.instance if form.is_valid() else None)
        
        if form.is_valid() and formset.is_valid():
            event = form.save()
            formset.instance = event
            formset.save()
            messages.success(request, "Event created successfully!")
            return redirect("home")
        else:
            messages.error(request, "Error creating event. Please check the form.")
            return render(request, "bets/create_event.html", {"form": form, "formset": formset})
    else:
        form = ImageUploadForm(label_suffix="")
        formset = EventOptionFormSet(instance=form.instance)

    return render(request, "bets/create_event.html", {"form": form, "formset": formset})


def service2(request):
    return render(request, "bets/service2.html")


def all_services(request):
    return render(request, "bets/all_services.html")


def profile(request):
    return render(request, "bets/profile.html")


def logout(request):
    logout(request)

    redirect("home")


def signup(request):
    return render(request, "bets/signup.html")


def login(request):
    return render(request, "bets/login.html")
