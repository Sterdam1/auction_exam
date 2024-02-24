from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# def view_Lot(request, model_id):
#     # Получить модель
#     model = get_object_or_404(Lot, pk=model_id)
#     # Проверить, что текущий пользователь имеет право на просмотр этой модели
#     if model.created_by != request.user:
#         # Если текущий пользователь не создавал эту модель, то вернуть ошибку доступа или выполнить другие действия
#         return HttpResponse("У вас нет прав для просмотра этой модели.")
#     else:
#         pass

from .forms import RegistrationForm

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            # Создаем нового пользователя с помощью данных из формы
            user = User.objects.create_user(username=username, password=password, email=email)
            user.is_staff = True
            user.is_superuser = False
            user.save()
            # Аутентифицируем и автоматически входим в систему
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('admin:index')  # Перенаправляем на административную панель
    else:
        form = RegistrationForm()
    return render(request, 'registration_form.html', {'form': form})