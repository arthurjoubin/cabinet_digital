from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from cabinet_digital.models import Integrator
import os


class Command(BaseCommand):
    help = 'Exporte tous les intégrateurs de la base de données vers un fichier texte'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='integrators_list.txt',
            help='Nom du fichier de sortie (défaut: integrators_list.txt)',
        )
        parser.add_argument(
            '--published-only',
            action='store_true',
            help='Exporter seulement les intégrateurs publiés',
        )

    def handle(self, *args, **options):
        queryset = Integrator.objects.all()
        
        if options['published_only']:
            queryset = queryset.filter(is_published=True)
            
        integrators = queryset.order_by('name')
        
        if not integrators.exists():
            self.stdout.write(self.style.WARNING('Aucun intégrateur trouvé dans la base de données.'))
            return
        
        output_file = options['output']
        filter_text = " (publiés uniquement)" if options['published_only'] else ""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f'LISTE DES INTÉGRATEURS{filter_text.upper()}\n')
            f.write(f'Nombre total: {integrators.count()}\n')
            f.write('=' * 80 + '\n\n')
            
            for i, integrator in enumerate(integrators, 1):
                f.write(f'[{i}] {integrator.name}\n')
                f.write(f'    Slug: {integrator.slug}\n')
                f.write(f'    Statut: {"✅ Publié" if integrator.is_published else "❌ Non publié"}\n')
                
                if integrator.is_top_pick:
                    f.write(f'    ⭐ Top Pick\n')
                
                if integrator.excerpt:
                    f.write(f'    Extrait: {integrator.excerpt}\n')
                
                if integrator.description:
                    # Nettoyer le HTML
                    clean_desc = strip_tags(integrator.description).strip()
                    f.write(f'    Description: {clean_desc}\n')
                
                if integrator.site:
                    f.write(f'    🌐 Site web: {integrator.site}\n')
                

                
                # Afficher les logiciels associés
                softwares = integrator.softwares.all()
                if softwares.exists():
                    software_names = ', '.join([s.name for s in softwares])
                    f.write(f'    💻 Logiciels ({softwares.count()}): {software_names}\n')
                
                # Afficher le nombre d'avis
                review_count = integrator.reviews.filter(status='published').count()
                if review_count > 0:
                    f.write(f'    ⭐ Avis publiés: {review_count}\n')
                
                f.write('\n' + '-' * 80 + '\n\n')
        
        self.stdout.write(
            self.style.SUCCESS(f'Liste des intégrateurs exportée vers: {os.path.abspath(output_file)}')
        ) 