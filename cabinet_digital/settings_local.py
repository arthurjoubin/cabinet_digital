"""
Configuration locale pour le développement.
Ce fichier doit être importé par settings.py uniquement en environnement de développement.
"""

def configure_for_development(settings_module):
    """
    Configure les paramètres pour le développement local.
    """
    # Uniquement des paramètres simples qui ne nécessitent pas l'accès aux modèles
    # Le reste de la configuration sera fait par les signaux ou manuellement
    settings_module.ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
    
    # Autres paramètres de développement peuvent être ajoutés ici
    return settings_module 