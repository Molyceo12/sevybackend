from django.apps import AppConfig


class SevyAppConfig(AppConfig):
    name = 'sevy_app'

    def ready(self):
        import sevy_app.signals
