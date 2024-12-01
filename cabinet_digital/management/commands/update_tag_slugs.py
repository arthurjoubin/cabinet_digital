from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cabinet_digital.models import Tag

class Command(BaseCommand):
    help = 'Met à jour les slugs des tags existants'

    def handle(self, *args, **options):
        tags = Tag.objects.all()
        for tag in tags:
            tag.slug = slugify(tag.name)
            tag.save()
        self.stdout.write(self.style.SUCCESS('Slugs des tags mis à jour avec succès')) 