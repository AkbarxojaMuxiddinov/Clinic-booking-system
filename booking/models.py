from django.db import models

# Create your models here.


from django.db import models

class Client(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    full_name = models.CharField(max_length=255, verbose_name="F.I.SH.")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    email = models.EmailField(verbose_name="Email manzili")

    def __str__(self):
        return f"{self.full_name} ({self.phone}"
    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"


class  Service(models.Model):
    name = models.CharField(max_length=255, verbose_name="Xizmat nomi")
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Narxi (so'm)")
    duration_minutes = models.IntegerField(default=60, verbose_name="Davomiyligi (daqiqa)")

    def __str__(self):
        return f"{self.name} ({self.price} so'm)"

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('canceled', 'Bekor qilindi'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="bookings", verbose_name="Mijoz")
    service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name="bookings", verbose_name="Xizmat")
    booking_date = models.DateTimeField(verbose_name="Qabul vaqti")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    ai_advice = models.TextField(blank=True, null=True, verbose_name="AI Tavsiyasi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")


    def __str__(self):
        return f"{self.client} {self.service} {self.booking_date}"

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
