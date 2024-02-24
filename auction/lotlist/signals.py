from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_migrate
from .models import ReadyOrNot
from django.db import models

@receiver(post_migrate)
def create_instances(sender, **kwargs):
    if sender.name == 'lotlist':
        ReadyOrNot.objects.bulk_create([ReadyOrNot(status='Лот готов к торгам'),
                                        ReadyOrNot(status='Лот готовиться к торгам')])
