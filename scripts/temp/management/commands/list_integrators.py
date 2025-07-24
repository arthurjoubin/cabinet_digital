from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from cabinet_digital.models import Integrator


class Command(BaseCommand):
    help = 'Liste tous les intégrateurs de la base de données avec leurs descriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--published-only',
            action='store_true',
            help='Afficher seulement les intégrateurs publiés',
        )
        parser.add_argument(
            '--full-description',
            action='store_true',
            help='Afficher la description complète (sans troncature)',
        )

    def handle(self, *args, **options):
        queryset = Integrator.objects.all()
        
        if options['published_only']:
            queryset = queryset.filter(is_published=True)
            
        integrators = queryset.order_by('name')
        
        if not integrators.exists():
            self.stdout.write(self.style.WARNING('Aucun intégrateur trouvé dans la base de données.'))
            return
        
        filter_text = " (publiés uniquement)" if options['published_only'] else ""
        self.stdout.write(self.style.SUCCESS(f'Nombre total d\'intégrateurs{filter_text}: {integrators.count()}\n'))
        
        for i, integrator in enumerate(integrators, 1):
            self.stdout.write(self.style.SUCCESS(f'[{i}] {integrator.name}'))
            self.stdout.write(f'    Slug: {integrator.slug}')
            self.stdout.write(f'    Statut: {"✅ Publié" if integrator.is_published else "❌ Non publié"}')
            
            if integrator.is_top_pick:
                self.stdout.write(f'    ⭐ Top Pick')
            
            if integrator.excerpt:
                self.stdout.write(f'    Extrait: {integrator.excerpt}')
            
            if integrator.description:
                # Nettoyer le HTML
                clean_desc = strip_tags(integrator.description).strip()
                if options['full_description']:
                    self.stdout.write(f'    Description: {clean_desc}')
                else:
                    # Limiter à 300 caractères pour l'affichage
                    desc = clean_desc[:300] + '...' if len(clean_desc) > 300 else clean_desc
                    self.stdout.write(f'    Description: {desc}')
            
            if integrator.site:
                self.stdout.write(f'    🌐 Site web: {integrator.site}')
            

            
            # Afficher les logiciels associés
            softwares = integrator.softwares.all()
            if softwares.exists():
                software_names = ', '.join([s.name for s in softwares])
                self.stdout.write(f'    💻 Logiciels ({softwares.count()}): {software_names}')
            
            # Afficher le nombre d'avis
            review_count = integrator.reviews.filter(status='published').count()
            if review_count > 0:
                self.stdout.write(f'    ⭐ Avis publiés: {review_count}')
            
            self.stdout.write('')  # Ligne vide pour séparer 