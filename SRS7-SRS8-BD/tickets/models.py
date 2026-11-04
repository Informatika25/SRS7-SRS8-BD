import django.conf
from django.db import models

# Create your models here.

class Category(models.Model):
    objects = None
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        PROGRESS = "progress", "В работе"
        DONE = "done", "Выполнена"

    title = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="tickets"
    )

    owner = models.ForeignKey(
        django.conf.settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    status = models.CharField(
        max_length= 20,
        choices=Status.choices,
        default=Status.NEW
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
