from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cabinet_digital.models import PlatformeDematerialisation, PDPSpecialtyTag


class Command(BaseCommand):
    help = 'Fusionner les tags PDP similaires pour réduire les doublons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait modifié sans rien modifier',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY RUN - Aucune modification ne sera effectuée'))

        # Définir les mappings de fusion des tags
        tag_mappings = {
            # GED et Gestion Documentaire
            'Gestion Documentaire': 'GED',
            
            # Expertise Comptable
            'Experts-Comptables': 'Expertise Comptable',
            
            # Facturation
            'Logiciel de Facturation': 'Facturation',
            'Facturation Électronique': 'Facturation',
            
            # Gestion
            'Logiciel de Gestion': 'Gestion',
            'Logiciel d\'Entreprise': 'Gestion',
            
            # PME et Indépendants
            'Indépendants/PME': 'PME',
            
            # Grandes Entreprises
            'ETI/GE': 'Grandes Entreprises',
            'ETI': 'Grandes Entreprises',
            
            # Digitalisation
            'Digitalisation B2B': 'Digitalisation',
            'Digitalisation des Processus': 'Digitalisation',
            'Dématérialisation': 'Digitalisation',
            
            # Échange de données
            'Échange de Documents Électroniques': 'EDI',
            'Échange de Données': 'EDI',
            
            # International
            'International (cloud)': 'International',
            'International (taxe)': 'International',
            
            # Gestion Financière
            'Optimisation Financière': 'Gestion Financière',
            'Gestion des Dépenses': 'Gestion Financière',
            'Pré-comptabilité': 'Comptabilité',
            
            # Communication
            'Communication Client': 'Communication',
            'Gestion du Courrier': 'Communication',
            
            # Autres simplifications
            'Compte Professionnel': 'Comptabilité',
            'Gestion du Poste Client': 'Gestion',
            'Gestion de l\'Information': 'Gestion',
        }

        self.stdout.write(f'Mappings de fusion définis pour {len(tag_mappings)} tags')

        # Récupérer toutes les PDP avec des spécialités
        pdps = PlatformeDematerialisation.objects.filter(is_published=True).exclude(specialty='')
        
        updated_count = 0
        
        for pdp in pdps:
            original_specialty = pdp.specialty
            tags = [tag.strip() for tag in pdp.specialty.split(',') if tag.strip()]
            
            # Appliquer les mappings
            new_tags = []
            changed = False
            
            for tag in tags:
                if tag in tag_mappings:
                    new_tag = tag_mappings[tag]
                    if new_tag not in new_tags:  # Éviter les doublons
                        new_tags.append(new_tag)
                    changed = True
                    self.stdout.write(f'  {pdp.name}: "{tag}" → "{new_tag}"')
                else:
                    if tag not in new_tags:  # Éviter les doublons
                        new_tags.append(tag)
            
            if changed:
                new_specialty = ', '.join(new_tags)
                updated_count += 1
                
                if not dry_run:
                    pdp.specialty = new_specialty
                    pdp.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Mis à jour: {pdp.name}')
                    )
                    self.stdout.write(f'  Avant: {original_specialty}')
                    self.stdout.write(f'  Après: {new_specialty}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'[DRY RUN] Mettrait à jour: {pdp.name}')
                    )
                    self.stdout.write(f'  Avant: {original_specialty}')
                    self.stdout.write(f'  Après: {new_specialty}')

        # Nettoyer les tags de spécialité orphelins
        if not dry_run:
            # Récupérer tous les tags utilisés après fusion
            specialty_fields = PlatformeDematerialisation.objects.filter(
                is_published=True
            ).exclude(
                specialty=''
            ).values_list(
                'specialty', flat=True
            ).distinct()

            all_used_tags = set()
            for specialty_field in specialty_fields:
                if specialty_field:
                    tags = [tag.strip() for tag in specialty_field.split(',') if tag.strip()]
                    all_used_tags.update(tags)

            # Supprimer les PDPSpecialtyTag qui ne sont plus utilisés
            unused_tags = PDPSpecialtyTag.objects.exclude(
                name__in=all_used_tags
            )
            
            if unused_tags.exists():
                unused_count = unused_tags.count()
                unused_tags.delete()
                self.stdout.write(
                    self.style.WARNING(f'🗑️  Supprimé {unused_count} tags de spécialité non utilisés')
                )

        # Résumé
        if not dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'✓ {updated_count} PDP mises à jour'))
            self.stdout.write('Exécutez la commande create_pdp_specialty_tags pour recréer les tags de spécialité')
        else:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'[DRY RUN] {updated_count} PDP seraient mises à jour')) 