"""
Commande Django pour effectuer un audit SEO complet du site
"""
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import Client
from django.db import models
from django.apps import apps
from django.conf import settings
import re
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import logging

# Import conditionnel pour bs4
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Effectue un audit SEO complet du site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage détaillé des résultats',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Tenter de corriger automatiquement les problèmes détectés',
        )
        parser.add_argument(
            '--check-urls',
            action='store_true',
            help='Vérifier les URLs et liens cassés',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.fix_issues = options['fix']
        self.check_urls = options['check_urls']
        
        self.stdout.write(self.style.SUCCESS('🔍 Démarrage de l\'audit SEO...'))
        
        # Statistiques globales
        self.issues = defaultdict(list)
        self.warnings = defaultdict(list)
        self.successes = defaultdict(list)
        
        # Exécuter les différents audits
        self.audit_meta_descriptions()
        self.audit_title_tags()
        self.audit_images()
        self.audit_structured_data()
        
        if self.check_urls:
            self.audit_broken_links()
        
        # Afficher le résumé
        self.display_summary()

    def audit_meta_descriptions(self):
        """Audit des descriptions SEO"""
        self.stdout.write('\n📝 Audit des descriptions SEO...')
        
        # Modèles avec champs SEO dédiés
        seo_models = [
            ('cabinet_digital.Tag', 'seo_description'),
            ('cabinet_digital.Metier', 'seo_description'),
        ]
        
        # Modèles utilisant description/excerpt pour SEO
        content_models = [
            ('cabinet_digital.Software', 'description'),
            ('cabinet_digital.SoftwareCategory', 'description'),
            ('cabinet_digital.Integrator', 'description'),
            # Company exclue - pas de SEO pour le moment
            # PlatformeDematerialisation exclue - pas de SEO pour le moment
        ]
        
        # Import nécessaire pour les fonctions de base de données
        from django.db.models.functions import Length
        
        # Audit des modèles avec champs SEO dédiés
        for model_path, field_name in seo_models:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                
                total = model.objects.count()
                missing = model.objects.filter(
                    models.Q(**{f"{field_name}__isnull": True}) | 
                    models.Q(**{f"{field_name}__exact": ""})
                ).count()
                
                # Méthode alternative pour vérifier la longueur (compatible SQLite)
                try:
                    # Récupérer tous les objets avec le champ rempli
                    objects_with_field = model.objects.exclude(
                        models.Q(**{f"{field_name}__isnull": True}) | 
                        models.Q(**{f"{field_name}__exact": ""})
                    )
                    
                    short = 0
                    long = 0
                    
                    # Vérifier la longueur en Python (plus lent mais compatible)
                    for obj in objects_with_field:
                        field_value = getattr(obj, field_name)
                        if field_value:
                            length = len(field_value)
                            if length < 120:
                                short += 1
                            elif length > 160:
                                long += 1
                                
                except Exception as e:
                    # Fallback complet
                    short = 0
                    long = 0
                    self.warnings['seo_descriptions'].append(
                        f"{model_name}: Impossible de vérifier la longueur des {field_name} ({e})"
                    )
                
                if missing > 0:
                    self.issues['seo_descriptions'].append(
                        f"{model_name}: {missing}/{total} objets sans {field_name}"
                    )
                
                if short > 0:
                    self.warnings['seo_descriptions'].append(
                        f"{model_name}: {short} {field_name} trop courtes (<120 caractères)"
                    )
                
                if long > 0:
                    self.warnings['seo_descriptions'].append(
                        f"{model_name}: {long} {field_name} trop longues (>160 caractères)"
                    )
                
                if missing == 0 and short == 0 and long == 0 and total > 0:
                    self.successes['seo_descriptions'].append(
                        f"{model_name}: Toutes les descriptions SEO sont optimales"
                    )
                    
            except Exception as e:
                self.issues['seo_descriptions'].append(
                    f"Erreur lors de l'audit de {model_path}: {e}"
                )
        
        # Audit des modèles utilisant description/excerpt
        for model_path, field_name in content_models:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                
                # Pour Software, ne vérifier que les objets publiés
                if model_name == 'Software':
                    total = model.objects.filter(is_published=True).count()
                    missing = model.objects.filter(
                        is_published=True
                    ).filter(
                        models.Q(**{f"{field_name}__isnull": True}) | 
                        models.Q(**{f"{field_name}__exact": ""})
                    ).count()
                else:
                    total = model.objects.count()
                    missing = model.objects.filter(
                        models.Q(**{f"{field_name}__isnull": True}) | 
                        models.Q(**{f"{field_name}__exact": ""})
                    ).count()
                
                if missing > 0:
                    self.warnings['content_descriptions'].append(
                        f"{model_name}: {missing}/{total} objets {'publiés ' if model_name == 'Software' else ''}sans {field_name} (utilisé pour SEO)"
                    )
                else:
                    self.successes['content_descriptions'].append(
                        f"{model_name}: Tous les objets {'publiés ' if model_name == 'Software' else ''}ont une {field_name}"
                    )
                    
            except Exception as e:
                self.issues['content_descriptions'].append(
                    f"Erreur lors de l'audit de {model_path}: {e}"
                )

    def audit_title_tags(self):
        """Audit des balises title"""
        self.stdout.write('\n🏷️  Audit des balises title...')
        
        if not HAS_BS4:
            self.warnings['title_tags'].append("BeautifulSoup non installé - audit HTML limité")
            return
        
        # Vérifier les templates principaux
        test_urls = [
            '/',
            '/logiciels/',
            '/categories/',
            '/integrateurs/',
            '/plateformes-dematerialisation/',
            '/actualites/',
        ]
        
        client = Client()
        
        for url in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title_tag = soup.find('title')
                    
                    if not title_tag:
                        self.issues['title_tags'].append(f"Balise title manquante: {url}")
                    else:
                        title_text = title_tag.get_text().strip()
                        
                        if len(title_text) == 0:
                            self.issues['title_tags'].append(f"Balise title vide: {url}")
                        elif len(title_text) < 30:
                            self.warnings['title_tags'].append(f"Title trop court ({len(title_text)} caractères): {url}")
                        elif len(title_text) > 60:
                            self.warnings['title_tags'].append(f"Title trop long ({len(title_text)} caractères): {url}")
                        else:
                            self.successes['title_tags'].append(f"Title optimal: {url}")
                            
            except Exception as e:
                self.issues['title_tags'].append(f"Erreur lors du test de {url}: {e}")

    def audit_images(self):
        """Audit des images"""
        self.stdout.write('\n🖼️  Audit des images...')
        
        # Vérifier les modèles avec des images (Company et PDP exclus)
        models_with_images = [
            ('cabinet_digital.Software', 'logo'),
            ('cabinet_digital.Integrator', 'logo'),
        ]
        
        for model_path, image_field in models_with_images:
            try:
                app_label, model_name = model_path.split('.')
                model = apps.get_model(app_label, model_name)
                
                # Pour Software, ne vérifier que les objets publiés
                if model_name == 'Software':
                    total = model.objects.filter(is_published=True).count()
                    missing_images = model.objects.filter(
                        is_published=True
                    ).filter(
                        **{f"{image_field}__isnull": True}
                    ).count() + model.objects.filter(
                        is_published=True
                    ).filter(
                        **{f"{image_field}__exact": ""}
                    ).count()
                else:
                    total = model.objects.count()
                    missing_images = model.objects.filter(
                        **{f"{image_field}__isnull": True}
                    ).count() + model.objects.filter(
                        **{f"{image_field}__exact": ""}
                    ).count()
                
                if missing_images > 0:
                    self.warnings['images'].append(
                        f"{model_name}: {missing_images}/{total} objets {'publiés ' if model_name == 'Software' else ''}sans image"
                    )
                else:
                    self.successes['images'].append(
                        f"{model_name}: Toutes les images sont présentes {'(objets publiés)' if model_name == 'Software' else ''}"
                    )
                    
            except Exception as e:
                self.issues['images'].append(f"Erreur lors de l'audit des images de {model_path}: {e}")
        
        # Note informative pour les modèles exclus
        self.stdout.write('   ℹ️  Company et PlatformeDematerialisation exclus de l\'audit images (pas d\'images requises pour le moment)')

    def audit_structured_data(self):
        """Audit des données structurées"""
        self.stdout.write('\n📊 Audit des données structurées...')
        
        client = Client()
        test_urls = [
            '/',
            '/logiciels/',
        ]
        
        for url in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    
                    # Vérifier la présence de JSON-LD
                    if 'application/ld+json' in content:
                        self.successes['structured_data'].append(f"Données structurées présentes: {url}")
                    else:
                        self.warnings['structured_data'].append(f"Données structurées manquantes: {url}")
                        
            except Exception as e:
                self.issues['structured_data'].append(f"Erreur lors de l'audit des données structurées de {url}: {e}")

    def audit_broken_links(self):
        """Audit des liens cassés"""
        self.stdout.write('\n🔗 Audit des liens cassés...')
        
        # Cette fonction nécessiterait un crawl plus approfondi
        # Pour l'instant, on vérifie juste quelques URLs importantes
        important_urls = [
            '/',
            '/logiciels/',
            '/categories/',
            '/integrateurs/',
            '/sitemap.xml',
            '/robots.txt',
        ]
        
        client = Client()
        
        for url in important_urls:
            try:
                response = client.get(url)
                if response.status_code == 404:
                    self.issues['broken_links'].append(f"Lien cassé: {url}")
                elif response.status_code == 500:
                    self.issues['broken_links'].append(f"Erreur serveur: {url}")
                else:
                    self.successes['broken_links'].append(f"URL accessible: {url}")
                    
            except Exception as e:
                self.issues['broken_links'].append(f"Erreur lors du test de {url}: {e}")

    def display_summary(self):
        """Affiche le résumé de l'audit"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📋 RÉSUMÉ DE L\'AUDIT SEO'))
        self.stdout.write('='*60)
        
        # Compter les problèmes
        total_issues = sum(len(issues) for issues in self.issues.values())
        total_warnings = sum(len(warnings) for warnings in self.warnings.values())
        total_successes = sum(len(successes) for successes in self.successes.values())
        
        self.stdout.write(f"\n📊 Statistiques globales:")
        self.stdout.write(f"   ✅ Succès: {total_successes}")
        self.stdout.write(f"   ⚠️  Avertissements: {total_warnings}")
        self.stdout.write(f"   ❌ Problèmes critiques: {total_issues}")
        
        # Afficher les détails si verbose
        if self.verbose:
            self.display_detailed_results()
        
        # Score SEO
        total_checks = total_issues + total_warnings + total_successes
        if total_checks > 0:
            score = int(((total_successes + total_warnings * 0.5) / total_checks) * 100)
            if score >= 90:
                color = self.style.SUCCESS
                emoji = "🟢"
            elif score >= 70:
                color = self.style.WARNING
                emoji = "🟡"
            else:
                color = self.style.ERROR
                emoji = "🔴"
            
            self.stdout.write(f"\n{emoji} Score SEO global: {color(f'{score}%')}")
        
        # Recommandations
        if total_issues > 0:
            self.stdout.write(f"\n🔧 Pour améliorer votre SEO:")
            self.stdout.write("   1. Corrigez les problèmes critiques en priorité")
            self.stdout.write("   2. Ajoutez les meta descriptions manquantes")
            self.stdout.write("   3. Optimisez la longueur des balises title")
            self.stdout.write("   4. Ajoutez des données structurées sur toutes les pages")

    def display_detailed_results(self):
        """Affiche les résultats détaillés"""
        
        # Problèmes critiques
        if self.issues:
            self.stdout.write(f"\n❌ PROBLÈMES CRITIQUES:")
            for category, problems in self.issues.items():
                self.stdout.write(f"\n  {category.replace('_', ' ').title()}:")
                for problem in problems:
                    self.stdout.write(f"    - {problem}")
        
        # Avertissements
        if self.warnings:
            self.stdout.write(f"\n⚠️  AVERTISSEMENTS:")
            for category, warnings in self.warnings.items():
                self.stdout.write(f"\n  {category.replace('_', ' ').title()}:")
                for warning in warnings:
                    self.stdout.write(f"    - {warning}")
        
        # Succès
        if self.successes:
            self.stdout.write(f"\n✅ POINTS POSITIFS:")
            for category, successes in self.successes.items():
                for success in successes:
                    self.stdout.write(f"    - {success}")