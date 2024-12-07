from django.core.management.base import BaseCommand
from django.utils.text import slugify
import unidecode
from cabinet_digital.models import Tag

class Command(BaseCommand):
    help = 'Met à jour les slugs des tags existants'

    def handle(self, *args, **options):
        tags = Tag.objects.all()
        for tag in tags:
            tag.slug = ''
            tag.save()
            self.stdout.write(f'Slug mis à jour pour le tag "{tag.name}": {tag.slug}') 