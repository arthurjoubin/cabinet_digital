from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Configure le site Django pour le développement local'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=1)
            old_domain = site.domain
            site.domain = 'localhost:8000'
            site.name = 'localhost'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Site modifié de {old_domain} à localhost:8000'))
        except Site.DoesNotExist:
            Site.objects.create(id=1, domain='localhost:8000', name='localhost')
            self.stdout.write(self.style.SUCCESS('Site créé: localhost:8000'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur: {e}')) 