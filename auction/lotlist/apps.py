from django.apps import AppConfig


class LotlistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lotlist'

    def ready(self):
        import lotlist.signals
