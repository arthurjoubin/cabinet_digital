#!/usr/bin/env python3
"""
Script de correction automatique pour PythonAnywhere
Usage: python fix_pythonanywhere.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*80}")
    print(f"🔧 {title}")
    print(f"{'='*80}")

def print_section(title):
    """Affiche une section formatée"""
    print(f"\n{'─'*60}")
    print(f"📋 {title}")
    print(f"{'─'*60}")

def run_command(command, description=""):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}")
    print(f"Commande: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Succès:\n{result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur: {e}")
        if e.stderr:
            print(f"Détails: {e.stderr}")
        return False, e.stderr

def create_env_file():
    """Crée ou met à jour le fichier .env"""
    print_section("Configuration du fichier .env")
    
    env_content = """# Variables d'environnement pour PythonAnywhere
SECRET_KEY=django-insecure-pythonanywhere-changez-cette-cle-12345
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=votre-domaine.pythonanywhere.com,cabinetdigital.fr,www.cabinetdigital.fr
DATABASE_URL=sqlite:///db.sqlite3

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Autres configurations
COMPRESS_ENABLED=True
COMPRESS_OFFLINE=True
"""
    
    if Path('.env').exists():
        print("⚠️  Fichier .env existant trouvé")
        backup_path = '.env.backup'
        Path('.env').rename(backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Fichier .env créé/mis à jour")
    print("⚠️  IMPORTANT: Modifiez les valeurs dans .env avec vos vraies données!")

def install_dependencies():
    """Installe toutes les dépendances"""
    print_section("Installation des dépendances")
    
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt non trouvé")
        return False
    
    # Mise à jour de pip
    run_command("python -m pip install --upgrade pip", "Mise à jour de pip")
    
    # Installation des dépendances
    success, _ = run_command("pip install -r requirements.txt", "Installation des dépendances")
    
    if not success:
        print("⚠️  Tentative d'installation individuelle des packages critiques...")
        critical_packages = [
            'Django>=5.0',
            'python-dotenv',
            'django-compressor',
            'pillow',
            'django-unfold',
            'gunicorn',
            'dj-database-url'
        ]
        
        for package in critical_packages:
            run_command(f"pip install {package}", f"Installation de {package}")
    
    return success

def setup_database():
    """Configure la base de données"""
    print_section("Configuration de la base de données")
    
    # Créer les migrations
    success, _ = run_command("python manage.py makemigrations", "Création des migrations")
    
    # Appliquer les migrations
    success, _ = run_command("python manage.py migrate", "Application des migrations")
    
    return success

def collect_static_files():
    """Collecte les fichiers statiques"""
    print_section("Collecte des fichiers statiques")
    
    # Créer le répertoire staticfiles s'il n'existe pas
    staticfiles_dir = Path('staticfiles')
    if not staticfiles_dir.exists():
        staticfiles_dir.mkdir(parents=True)
        print("✅ Répertoire staticfiles créé")
    
    # Collecte des fichiers statiques
    success, _ = run_command("python manage.py collectstatic --noinput", "Collecte des fichiers statiques")
    
    if not success:
        print("⚠️  Tentative de collecte avec clear...")
        success, _ = run_command("python manage.py collectstatic --clear --noinput", "Collecte avec nettoyage")
    
    return success

def check_wsgi_config():
    """Vérifie la configuration WSGI"""
    print_section("Vérification WSGI")
    
    wsgi_content = """# WSGI configuration file for PythonAnywhere
import os
import sys

# Add your project directory to the Python path
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django and setup
import django
django.setup()

# Import the WSGI application
from config.wsgi import application
"""
    
    print("📋 Configuration WSGI recommandée pour PythonAnywhere:")
    print(wsgi_content)
    
    # Vérifier que le fichier wsgi.py existe
    wsgi_path = Path('config/wsgi.py')
    if wsgi_path.exists():
        print("✅ Fichier config/wsgi.py trouvé")
    else:
        print("❌ Fichier config/wsgi.py MANQUANT")

def create_pythonanywhere_wsgi():
    """Crée un fichier WSGI spécifique pour PythonAnywhere"""
    print_section("Création du fichier WSGI PythonAnywhere")
    
    wsgi_content = """# WSGI configuration file for PythonAnywhere
# Remplacez 'yourusername' par votre nom d'utilisateur PythonAnywhere
# Remplacez 'cabinetdigital' par le nom de votre projet

import os
import sys

# Add your project directory to the Python path
path = '/home/yourusername/cabinetdigital'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Load environment variables from .env file
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(path) / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Import Django and setup
import django
django.setup()

# Import the WSGI application
from config.wsgi import application

# This is the WSGI application object
# PythonAnywhere will use this
"""
    
    with open('wsgi_pythonanywhere.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Fichier wsgi_pythonanywhere.py créé")
    print("⚠️  IMPORTANT: Modifiez le chemin dans le fichier avec votre nom d'utilisateur!")

def test_django_setup():
    """Teste la configuration Django"""
    print_section("Test de la configuration Django")
    
    try:
        # Test d'import Django
        import django
        print(f"✅ Django version: {django.get_version()}")
        
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        # Test des settings
        from django.conf import settings
        print(f"✅ Settings chargés - DEBUG: {settings.DEBUG}")
        
        # Test de l'application WSGI
        from config.wsgi import application
        print("✅ Application WSGI importée")
        
        # Test des vérifications Django
        from django.core.management import execute_from_command_line
        print("🔄 Exécution des vérifications Django...")
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Vérifications Django réussies")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test Django: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_deployment_checklist():
    """Crée une checklist de déploiement"""
    print_section("Création de la checklist de déploiement")
    
    checklist_content = """# Checklist de déploiement PythonAnywhere

## 1. Fichiers de configuration
- [ ] .env configuré avec les bonnes valeurs
- [ ] requirements.txt à jour
- [ ] wsgi_pythonanywhere.py configuré avec le bon chemin

## 2. Base de données
- [ ] Migrations créées: `python manage.py makemigrations`
- [ ] Migrations appliquées: `python manage.py migrate`
- [ ] Superuser créé: `python manage.py createsuperuser`

## 3. Fichiers statiques
- [ ] Collecte effectuée: `python manage.py collectstatic --noinput`
- [ ] Répertoire staticfiles créé et accessible

## 4. Configuration PythonAnywhere
- [ ] Application web créée sur PythonAnywhere
- [ ] Fichier WSGI configuré dans l'interface web
- [ ] Variables d'environnement définies
- [ ] Domaine configuré (si applicable)

## 5. Tests
- [ ] `python manage.py check` sans erreur
- [ ] Site accessible via l'URL PythonAnywhere
- [ ] Admin accessible
- [ ] Fichiers statiques chargés

## 6. Sécurité
- [ ] SECRET_KEY unique et sécurisée
- [ ] DEBUG=False en production
- [ ] ALLOWED_HOSTS configuré correctement
- [ ] Certificat SSL activé (si domaine personnalisé)

## Variables d'environnement importantes
```
SECRET_KEY=votre-cle-secrete-unique
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=votre-domaine.pythonanywhere.com,cabinetdigital.fr,www.cabinetdigital.fr
```

## Commandes utiles
```bash
# Redémarrer l'application
# Via l'interface web PythonAnywhere

# Voir les logs
# Via l'interface web: Files > /var/log/

# Tester la configuration
python manage.py check

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist_content)
    
    print("✅ Checklist de déploiement créée: DEPLOYMENT_CHECKLIST.md")

def main():
    """Fonction principale"""
    print_header("CORRECTION AUTOMATIQUE PYTHONANYWHERE")
    
    print(f"📂 Répertoire de travail: {os.getcwd()}")
    
    # Vérifier la structure du projet
    if not Path('manage.py').exists():
        print("❌ manage.py non trouvé. Êtes-vous dans le bon répertoire ?")
        return
    
    print("✅ Projet Django détecté")
    
    # Étapes de correction
    steps = [
        ("Création du fichier .env", create_env_file),
        ("Installation des dépendances", install_dependencies),
        ("Configuration de la base de données", setup_database),
        ("Collecte des fichiers statiques", collect_static_files),
        ("Vérification WSGI", check_wsgi_config),
        ("Création du fichier WSGI PythonAnywhere", create_pythonanywhere_wsgi),
        ("Test de la configuration Django", test_django_setup),
        ("Création de la checklist", create_deployment_checklist),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for description, function in steps:
        try:
            print_header(description)
            result = function()
            if result is not False:  # None ou True = succès
                success_count += 1
                print(f"✅ {description} - TERMINÉ")
            else:
                print(f"⚠️  {description} - ÉCHEC PARTIEL")
        except Exception as e:
            print(f"❌ Erreur lors de {description}: {e}")
            import traceback
            traceback.print_exc()
    
    # Résumé final
    print_header("RÉSUMÉ DE LA CORRECTION")
    print(f"📊 Étapes réussies: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("🎉 Toutes les corrections ont été appliquées avec succès!")
    else:
        print("⚠️  Certaines corrections ont échoué. Vérifiez les messages ci-dessus.")
    
    print("\n📋 Actions manuelles restantes:")
    print("1. Modifiez le fichier .env avec vos vraies valeurs")
    print("2. Configurez l'application web sur PythonAnywhere")
    print("3. Uploadez le fichier wsgi_pythonanywhere.py dans l'interface web")
    print("4. Redémarrez l'application web")
    print("5. Testez votre site")
    
    print("\n📄 Consultez DEPLOYMENT_CHECKLIST.md pour plus de détails")

if __name__ == "__main__":
    main() 