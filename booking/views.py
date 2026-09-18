from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Service, Client, Booking


def index(request):
    services = Service.objects.all()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        service_id = request.POST.get("service_id")
        booking_date = request.POST.get("booking_date")


        client, _ = Client.objects.get_or_create(
            email=email,
            defaults={'full_name': full_name, 'phone': phone, 'telegram_id': 0}
        )

        service = Service.objects.get(id=service_id)


        Booking.objects.create(
            client=client,
            service=service,
            booking_date=booking_date
        )

        messages.success(request, "Qabulga muvaffaqiyatli yozildingiz!")
        return redirect("index")

    return render(request, "booking/index.html", {"services": services})
