from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cabinet_digital.models import PlatformeDematerialisation, PDPSpecialtyTag


class Command(BaseCommand):
    help = 'Créer automatiquement les tags de spécialité PDP à partir des données existantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait créé sans rien créer',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Mettre à jour les tags existants avec du contenu SEO par défaut',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_existing = options['update_existing']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY RUN - Aucune modification ne sera effectuée'))

        # Récupérer toutes les spécialités existantes des PDP
        specialty_fields = PlatformeDematerialisation.objects.filter(
            is_published=True
        ).exclude(
            specialty=''
        ).values_list(
            'specialty', flat=True
        ).distinct()

        # Extraire les tags individuels des champs séparés par des virgules
        all_specialties = set()
        for specialty_field in specialty_fields:
            if specialty_field:
                tags = [tag.strip() for tag in specialty_field.split(',') if tag.strip()]
                all_specialties.update(tags)

        self.stdout.write(f'Trouvé {len(all_specialties)} spécialités uniques')

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for specialty_name in sorted(all_specialties):
            slug = slugify(specialty_name)
            
            # Compter le nombre de PDP avec cette spécialité
            pdp_count = PlatformeDematerialisation.objects.filter(
                specialty__icontains=specialty_name,
                is_published=True
            ).count()

            try:
                tag, created = PDPSpecialtyTag.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': specialty_name,
                        'seo_title': f'PDP spécialisées en {specialty_name} - Facturation électronique',
                        'seo_description': f'Découvrez {pdp_count} Plateformes de Dématérialisation Partenaires spécialisées en {specialty_name}. Solutions certifiées pour la facturation électronique obligatoire.',
                        'seo_content': f'<h2>Qu\'est-ce qu\'une PDP spécialisée en {specialty_name} ?</h2>\n<p>Les Plateformes de Dématérialisation Partenaires (PDP) spécialisées en {specialty_name} sont des solutions certifiées par l\'administration fiscale française pour permettre aux entreprises de respecter l\'obligation de facturation électronique.</p>\n<p>Ces plateformes offrent des fonctionnalités spécialement adaptées aux besoins des entreprises du secteur {specialty_name}.</p>',
                        'is_published': True
                    }
                )

                if not dry_run:
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Créé: {specialty_name} (slug: {slug}) - {pdp_count} PDP')
                        )
                    else:
                        if update_existing and not tag.seo_title:
                            # Mettre à jour les tags existants qui n'ont pas de contenu SEO
                            tag.seo_title = f'PDP spécialisées en {specialty_name} - Facturation électronique'
                            tag.seo_description = f'Découvrez {pdp_count} Plateformes de Dématérialisation Partenaires spécialisées en {specialty_name}. Solutions certifiées pour la facturation électronique obligatoire.'
                            tag.seo_content = f'<h2>Qu\'est-ce qu\'une PDP spécialisée en {specialty_name} ?</h2>\n<p>Les Plateformes de Dématérialisation Partenaires (PDP) spécialisées en {specialty_name} sont des solutions certifiées par l\'administration fiscale française pour permettre aux entreprises de respecter l\'obligation de facturation électronique.</p>\n<p>Ces plateformes offrent des fonctionnalités spécialement adaptées aux besoins des entreprises du secteur {specialty_name}.</p>'
                            tag.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'↻ Mis à jour: {specialty_name} (slug: {slug}) - {pdp_count} PDP')
                            )
                        else:
                            skipped_count += 1
                            self.stdout.write(f'- Existe déjà: {specialty_name} (slug: {slug}) - {pdp_count} PDP')
                else:
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'[DRY RUN] Créerait: {specialty_name} (slug: {slug}) - {pdp_count} PDP')
                        )
                        created_count += 1
                    else:
                        self.stdout.write(f'[DRY RUN] Existe déjà: {specialty_name} (slug: {slug}) - {pdp_count} PDP')
                        skipped_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erreur avec {specialty_name}: {str(e)}')
                )

        # Résumé
        if not dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(f'✓ {created_count} tags créés'))
            if update_existing:
                self.stdout.write(self.style.WARNING(f'↻ {updated_count} tags mis à jour'))
            self.stdout.write(f'- {skipped_count} tags existants ignorés')
        else:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'[DRY RUN] {created_count} tags seraient créés'))
            self.stdout.write(f'[DRY RUN] {skipped_count} tags existent déjà') 