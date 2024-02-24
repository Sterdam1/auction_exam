from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms



class ImageAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
            if request.user.is_superuser:
                return ()
            return ('created_by',) 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Если пользователь не является суперпользователем, фильтруем объекты по создавшему их пользователю
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs
     
    def has_change_permission(self, request, obj=None):
        # Проверяем, имеет ли пользователь право на изменение объекта
        if obj is not None and not request.user.is_superuser and obj.created_by != request.user:
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.save()


class LotAdmin(admin.ModelAdmin):
    filter_horizontal = ['img']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'img' and not request.user.is_superuser:
            kwargs['queryset'] = Image.objects.filter(created_by=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ('created_by',) 
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Если пользователь не является суперпользователем, фильтруем объекты по создавшему их пользователю
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs

    def has_change_permission(self, request, obj=None):
        # Проверяем, имеет ли пользователь право на изменение объекта
        if obj is not None and not request.user.is_superuser and obj.created_by != request.user:
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.save()


class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Фильтруем пользователей по текущему пользователю
        if not request.user.is_superuser:
            return qs.filter(id=request.user.id)
        else: 
            return qs.filter()
        
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Убираем раздел "Permissions" для не суперпользователей
        if not request.user.is_superuser:
            fieldsets = [(None, {'fields': ('username', 'password')}),
                         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
                         ('Important dates', {'fields': ('last_login', 'date_joined')})]
        return fieldsets

class UserFinanceAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Если пользователь не является суперпользователем, фильтруем объекты по создавшему их пользователю
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
    
    def has_change_permission(self, request, obj=None):
        # Проверяем, имеет ли пользователь право на изменение объекта
        if obj is not None and not request.user.is_superuser and obj.user != request.user:
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        obj.save()    

class ReportsAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
            return ('reported_username', 'user_that_reported', 'cause') 
    
class HistoryAdmin(admin.ModelAdmin):
     def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Если пользователь не является суперпользователем, фильтруем объекты по создавшему их пользователю
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs 


admin.site.unregister(User)  # Сначала снимаем стандартную регистрацию
admin.site.register(User, CustomUserAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(Report, ReportsAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(UserFinance, UserFinanceAdmin)
admin.site.register(SellHistory, HistoryAdmin)
admin.site.register(Strikes)