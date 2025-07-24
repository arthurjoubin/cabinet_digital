from django.apps import AppConfig


class CabinetDigitalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cabinet_digital'
    label = 'cabinet_digital'  # Ceci définit le préfixe des tables de base de données
    