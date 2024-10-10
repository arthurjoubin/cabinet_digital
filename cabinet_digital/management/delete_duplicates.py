import sys
import os
import django
from django.conf import settings
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cabinet_digital.settings")
django.setup()

from django.core.management.base import BaseCommand
from cabinet_digital.models import Software
from django.db.models import Count
from django.db import connection

class Command(BaseCommand):
    help = 'Supprime les entrées de logiciels en double basées sur le nom'

    def handle(self, *args, **options):
        # Verification of the database used
        self.stdout.write(f"Utilisation de la base de données : {settings.DATABASES['default']['NAME']}")
        logging.debug(f"Using database: {settings.DATABASES['default']['NAME']}")

        duplicates = Software.objects.values('name').annotate(count=Count('id')).filter(count__gt=1)
        logging.debug(f"Found {len(duplicates)} duplicate entries")

        for duplicate in duplicates:
            softwares = Software.objects.filter(name=duplicate['name']).order_by('id')
            logging.debug(f"Processing duplicates for '{duplicate['name']}': {duplicate['count']} entries")
            
            # Garder le premier, supprimer les autres
            first_software = softwares.first()
            for software in softwares[1:]:
                logging.debug(f"Deleting software with id {software.id}")
                software.delete()
            
            # Vérifier la suppression
            remaining = Software.objects.filter(name=duplicate['name']).count()
            if remaining == 1:
                self.stdout.write(f"Suppression réussie de {duplicate['count'] - 1} doublons de '{duplicate['name']}'")
                logging.info(f"Suppression réussie de {duplicate['count'] - 1} doublons de '{duplicate['name']}'")
            else:
                self.stdout.write(self.style.WARNING(f"Échec de la suppression de tous les doublons de '{duplicate['name']}'. {remaining} entrées restantes."))
                logging.warning(f"Échec de la suppression de tous les doublons de '{duplicate['name']}'. {remaining} entrées restantes.")

        self.stdout.write(self.style.SUCCESS('Processus de suppression des doublons terminé'))
        logging.info('Processus de suppression des doublons terminé')