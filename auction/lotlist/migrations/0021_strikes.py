# Generated by Django 5.0.2 on 2024-02-24 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotlist', '0020_rename_sell_history_sellhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Strikes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Введите имя пользователя в телеграмме', max_length=100, verbose_name='Имя пользователя в телеграмме')),
                ('strikes', models.IntegerField(choices=[(1, 'Один'), (2, 'Два'), (3, 'Три')])),
            ],
        ),
    ]
