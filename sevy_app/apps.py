from django.apps import AppConfig


class SevyAppConfig(AppConfig):
    name = 'sevy_app'

    def ready(self):
        import sevy_app.signals
        
        # Initialize Firebase Admin SDK on startup
        from sevy_app.firebase.firebase_setup import initialize_firebase
        initialize_firebase()
