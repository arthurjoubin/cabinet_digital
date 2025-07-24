from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cabinet_digital.models import Software, SoftwareCategory, Company
from django.db import transaction

class Command(BaseCommand):
    help = 'Add missing software solutions mentioned in integrator partnerships'

    def handle(self, *args, **options):
        # Get or create default category
        default_category, _ = SoftwareCategory.objects.get_or_create(
            slug='erp-gestion',
            defaults={
                'name': 'ERP et Gestion',
                'description': 'Solutions de planification des ressources d\'entreprise et de gestion',
                'is_published': True
            }
        )

        missing_software = [
            # Divalto solutions
            {
                'name': 'Divalto Infinity',
                'description': '<p>ERP couvrant l\'ensemble des fonctions clés de l\'entreprise : gestion commerciale, CRM, achats, production, finances, paie et RH, gestion à l\'affaire, WMS, gestion de la maintenance, système de qualité. Adaptable aux spécificités de l\'activité, interfaçable avec des applications tierces, et disponible en mode SaaS sur un cloud dédié.</p>',
                'excerpt': 'ERP complet couvrant toutes les fonctions clés de l\'entreprise, adaptable et disponible en SaaS.',
                'company_name': 'Divalto'
            },
            {
                'name': 'Divalto Weavy',
                'description': '<p>Solution CRM de Divalto pour la gestion de la relation client, intégrée à l\'écosystème Divalto Infinity.</p>',
                'excerpt': 'Solution CRM intégrée à l\'écosystème Divalto pour la gestion de la relation client.',
                'company_name': 'Divalto'
            },
            # Infor solutions
            {
                'name': 'Infor Anael Finance',
                'description': '<p>Premier ERP dédié à la DAF en France. Solution complète incluant la comptabilité, la trésorerie, la conformité et la numérisation des processus pour les départements financiers. Offre des fonctionnalités avancées de dématérialisation, facturation électronique et rapprochement assisté par l\'IA.</p>',
                'excerpt': '1er ERP dédié à la DAF en France, spécialisé comptabilité, trésorerie et conformité.',
                'company_name': 'Infor'
            },
            {
                'name': 'Infor Anael RH',
                'description': '<p>Solution de gestion des ressources humaines d\'Infor, intégrée à l\'écosystème Anael pour une gestion complète des RH.</p>',
                'excerpt': 'Solution RH intégrée à l\'écosystème Infor Anael pour la gestion des ressources humaines.',
                'company_name': 'Infor'
            },
            # Microsoft solutions
            {
                'name': 'Microsoft Dynamics 365',
                'description': '<p>Suite d\'applications métier cloud de Microsoft incluant ERP (Business Central), CRM (Sales, Service Client, Marketing) et autres applications de gestion d\'entreprise. Solution intégrée pour la transformation numérique des PME et ETI.</p>',
                'excerpt': 'Suite d\'applications métier cloud Microsoft : ERP, CRM et gestion d\'entreprise intégrée.',
                'company_name': 'Microsoft'
            },
            {
                'name': 'Microsoft Power BI',
                'description': '<p>Plateforme de Business Intelligence de Microsoft pour l\'analyse de données et la création de tableaux de bord interactifs. Permet de transformer les données en informations exploitables pour la prise de décision.</p>',
                'excerpt': 'Plateforme BI Microsoft pour l\'analyse de données et tableaux de bord interactifs.',
                'company_name': 'Microsoft'
            },
            {
                'name': 'Microsoft Business Central',
                'description': '<p>Solution ERP cloud de Microsoft conçue pour les PME. Intègre la gestion financière, commerciale, des achats, des stocks, de la production et des projets dans une solution unifiée.</p>',
                'excerpt': 'ERP cloud Microsoft pour PME : gestion financière, commerciale et opérationnelle unifiée.',
                'company_name': 'Microsoft'
            },
            # Oracle solutions
            {
                'name': 'Oracle JD Edwards',
                'description': '<p>Suite ERP d\'Oracle pour les entreprises moyennes et grandes. Couvre la gestion financière, la chaîne d\'approvisionnement, la fabrication et la gestion de projets avec des fonctionnalités avancées pour les opérations complexes.</p>',
                'excerpt': 'Suite ERP Oracle pour entreprises moyennes et grandes, gestion complète des opérations.',
                'company_name': 'Oracle'
            },
            {
                'name': 'NetSuite',
                'description': '<p>ERP Cloud numéro 1 mondial d\'Oracle. Solution complète intégrant ERP, CRM, e-commerce et gestion financière dans une plateforme cloud unifiée. Idéale pour les entreprises en croissance.</p>',
                'excerpt': 'ERP Cloud #1 mondial Oracle : solution complète ERP, CRM, e-commerce en cloud unifié.',
                'company_name': 'Oracle'
            },
            # Other solutions
            {
                'name': 'Everwin',
                'description': '<p>Logiciel de gestion leader sur le marché de la gestion opérationnelle et administrative des entreprises. Propose des solutions sectorielles spécifiques comme Everwin GX (prestataires de services), GX-BTP (construction), SX (PME/ETI).</p>',
                'excerpt': 'Leader de la gestion opérationnelle et administrative avec solutions sectorielles spécialisées.',
                'company_name': 'Everwin'
            },
            {
                'name': 'MyReport',
                'description': '<p>Solution de Business Intelligence qui transforme les données en décisions stratégiques grâce à une intégration facile, une collecte de données automatisée, des rapports dynamiques et une analyse prédictive.</p>',
                'excerpt': 'Solution BI pour transformer les données en décisions avec rapports dynamiques et analyse prédictive.',
                'company_name': 'MyReport'
            },
            {
                'name': 'Esker',
                'description': '<p>Plateforme cloud mondiale pour l\'automatisation des cycles de gestion, notamment la dématérialisation des factures et l\'automatisation des processus Procure-to-Pay et Order-to-Cash.</p>',
                'excerpt': 'Plateforme cloud d\'automatisation des cycles de gestion et dématérialisation des factures.',
                'company_name': 'Esker'
            },
            {
                'name': 'HubSpot',
                'description': '<p>Plateforme CRM et marketing automation leader mondial. Offre des outils intégrés pour le marketing, les ventes, le service client et la gestion de contenu.</p>',
                'excerpt': 'Plateforme CRM et marketing automation leader avec outils intégrés marketing, ventes et service.',
                'company_name': 'HubSpot'
            },
            {
                'name': 'Jedox',
                'description': '<p>Plateforme de planification et de gestion de la performance d\'entreprise (EPM). Combine planification financière, budgétisation, reporting et analyse dans une solution intégrée.</p>',
                'excerpt': 'Plateforme EPM pour planification financière, budgétisation et gestion de la performance.',
                'company_name': 'Jedox'
            },
            {
                'name': 'Avalara',
                'description': '<p>Solution de traitement des taxes en ligne, spécialisée dans l\'automatisation du calcul et de la gestion des taxes. S\'intègre avec de nombreux ERP pour des calculs fiscaux automatisés et précis.</p>',
                'excerpt': 'Solution d\'automatisation du calcul et de la gestion des taxes, intégration ERP.',
                'company_name': 'Avalara'
            },
            {
                'name': 'Open-Prod',
                'description': '<p>ERP de nouvelle génération conçu pour répondre aux besoins spécifiques des entreprises manufacturières. Flexible, adaptable et évolutif, couvre un large éventail de fonctionnalités de la production à la distribution.</p>',
                'excerpt': 'ERP nouvelle génération pour entreprises manufacturières, flexible et évolutif.',
                'company_name': 'Open-Prod'
            },
            {
                'name': 'Mautic',
                'description': '<p>Plateforme open source d\'automatisation marketing avec fonctionnalités d\'intelligence artificielle pour optimiser les campagnes e-mail et les temps d\'envoi.</p>',
                'excerpt': 'Plateforme open source d\'automatisation marketing avec IA pour optimiser les campagnes.',
                'company_name': 'Mautic'
            }
        ]

        self.stdout.write(self.style.SUCCESS('Début de l\'ajout des logiciels manquants...'))

        with transaction.atomic():
            for software_data in missing_software:
                # Create or get company
                company = None
                if software_data['company_name']:
                    company, created = Company.objects.get_or_create(
                        slug=slugify(software_data['company_name']),
                        defaults={
                            'name': software_data['company_name'],
                            'is_published': True
                        }
                    )
                    if created:
                        self.stdout.write(f'  ✓ Créé l\'entreprise: {company.name}')

                # Create or update software
                software, created = Software.objects.get_or_create(
                    slug=slugify(software_data['name']),
                    defaults={
                        'name': software_data['name'],
                        'description': software_data['description'],
                        'excerpt': software_data['excerpt'],
                        'company': company,
                        'is_published': True
                    }
                )

                if created:
                    # Add to default category
                    software.category.add(default_category)
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Créé le logiciel: {software.name}'))
                else:
                    # Update existing software
                    software.description = software_data['description']
                    software.excerpt = software_data['excerpt']
                    if company and not software.company:
                        software.company = company
                    software.save()
                    self.stdout.write(f'  ✓ Mis à jour le logiciel: {software.name}')

        self.stdout.write(self.style.SUCCESS('Ajout des logiciels terminé avec succès!')) 