from django.apps import AppConfig


class CabinetDigitalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cabinet_digital'
    
    def ready(self):
        # Import signals
        import cabinet_digital.signals 