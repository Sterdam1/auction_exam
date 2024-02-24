from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

class Image(models.Model):
    img = models.ImageField(upload_to='', verbose_name='Изображение лота', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.img.name

class ReadyOrNot(models.Model):
    status = models.TextField(max_length=20, verbose_name='Статус лота')
    
    def __str__(self):
        return self.status

class UserFinance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(help_text='Введите баланс', verbose_name='Баланс', default=500.0)

    def __str__(self):
        return self.user.username

class Report(models.Model):
    reported_username = models.CharField(max_length=100, verbose_name='Ник зарепорченого')
    user_that_reported = models.CharField(max_length=100, verbose_name='Ник человека, который зарепортил')
    cause = models.TextField(verbose_name='Причина')
    
    def __str__(self):
        return f'{self.user_that_reported} зарепортил {self.reported_username}'

class Lot(models.Model):
    img = models.ManyToManyField(Image)
    lot_name = models.CharField(max_length=200, help_text='Введите название лота', verbose_name='Название лота')
    start_price = models.FloatField(help_text='Введите начальную цену в долларах', verbose_name='Начальная цена')
    seller_link = models.CharField(max_length=200, help_text='Введите телеграмм ник', verbose_name='Телеграмм ник')
    lot_geo = models.CharField(max_length=200, help_text='Введите геолокацию лота', verbose_name='Адрес')
    lot_description = models.TextField(help_text='Добавьте описание к лоту', verbose_name='Описание')
    start_time = models.DateTimeField(help_text='Укажите время начала аукциона', verbose_name='Время начала аукциона', blank=True, null=True)
    end_time = models.DateTimeField(help_text='Укажите время окончания аукциона', verbose_name='Время окончания аукциона', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    ready_status = models.ForeignKey(ReadyOrNot, verbose_name='Готовность лота', on_delete=models.CASCADE, default=None)

    def clean(self):
        if self.start_time != None:
            if self.start_time < timezone.now():
                raise ValidationError("Start time cannot be in the past")

    def save(self, *args, **kwargs):
        self.full_clean()  # Perform clean() before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.lot_name


class SellHistory(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Продавеч')
    buyer = models.CharField(max_length=100, verbose_name='Покупатель') 
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, verbose_name='Лот')
    price = models.FloatField(verbose_name='Цена продажи')
    sell_date = models.DateField(verbose_name='Время продажи', blank=True, null=True)

    def __str__(self):
        return self.lot.lot_name
    

class Strikes(models.Model):
    choose = (
        (1, 'Один'),
        (2, 'Два'),
        (3, 'Три')
    )
    username = models.CharField(max_length=100, verbose_name='Имя пользователя в телеграмме', help_text='Введите имя пользователя в телеграмме')
    strikes = models.IntegerField(choices=choose)

    def __str__(self):
        return self.username