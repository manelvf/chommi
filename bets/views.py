from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf.urls.static import static

from .forms import ImageUploadForm


def index(request):
    gallery_images = [
        {
            "url": static("images/image1.jpg"),
            "alt": "First Image",
            "title": "Amazing Landscape",
            "description": "A beautiful scene from our collection",
        },
        # Add more images...
    ]

    return render(request, "gallery.html", {"gallery_images": gallery_images})

    return render(request, "bets/index.html")


def about(request):
    return render(request, "bets/about.html")


def create_event(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image uploaded successfully!")
            return redirect("upload_image")
    else:
        form = ImageUploadForm()

    return render(request, "upload_image.html", {"form": form})


def service2(request):
    return render(request, "bets/service2.html")


def all_services(request):
    return render(request, "bets/all_services.html")


def profile(request):
    return render(request, "bets/profile.html")


def logout(request):
    logout(request)

    redirect("home")
