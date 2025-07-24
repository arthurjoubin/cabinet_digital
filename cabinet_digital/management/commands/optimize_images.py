"""
Commande Django pour optimiser automatiquement les images du site
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from ...utils import convert_to_webp 
import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimise automatiquement toutes les images du site (conversion WebP, redimensionnement)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Modèle spécifique à traiter (ex: Software, Company)',
        )
        parser.add_argument(
            '--field',
            type=str,
            help='Champ image spécifique à traiter (ex: logo)',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='Qualité de compression WebP (0-100, défaut: 85)',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1200,
            help='Largeur maximale pour les images (défaut: 1200px)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans modification des fichiers',
        )

    def handle(self, *args, **options):
        self.quality = options['quality']
        self.max_width = options['max_width']
        self.dry_run = options['dry_run']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('🔍 Mode simulation - aucune modification ne sera effectuée'))
        
        self.stdout.write(self.style.SUCCESS('🖼️  Démarrage de l\'optimisation des images...'))
        
        # Statistiques
        self.processed = 0
        self.optimized = 0
        self.errors = 0
        
        # Modèles avec des champs image
        models_with_images = [
            ('cabinet_digital', 'Software', 'logo'),
            ('cabinet_digital', 'Company', 'logo'),
            ('cabinet_digital', 'Integrator', 'logo'),
            ('cabinet_digital', 'PlatformeDematerialisation', 'logo'),
        ]
        
        # Filtrer si un modèle/champ spécifique est demandé
        if options['model'] or options['field']:
            if options['model'] and options['field']:
                models_with_images = [
                    (app, model, field) for app, model, field in models_with_images
                    if model == options['model'] and field == options['field']
                ]
            elif options['model']:
                models_with_images = [
                    (app, model, field) for app, model, field in models_with_images
                    if model == options['model']
                ]
        
        # Traiter chaque modèle
        for app_label, model_name, field_name in models_with_images:
            self.process_model(app_label, model_name, field_name)
        
        # Afficher le résumé
        self.display_summary()

    def process_model(self, app_label, model_name, field_name):
        """Traite les images d'un modèle spécifique"""
        try:
            model = apps.get_model(app_label, model_name)
            objects_with_images = model.objects.exclude(**{f"{field_name}__isnull": True}).exclude(**{f"{field_name}__exact": ""})
            
            self.stdout.write(f"\n📂 Traitement de {model_name}.{field_name} ({objects_with_images.count()} images)...")
            
            for obj in objects_with_images:
                image_field = getattr(obj, field_name)
                if image_field and hasattr(image_field, 'path'):
                    self.process_image(image_field, f"{model_name} #{obj.pk}")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur lors du traitement de {model_name}.{field_name}: {e}")
            )
            self.errors += 1

    def process_image(self, image_field, context=""):
        """Traite une image individuelle"""
        try:
            original_path = image_field.path
            
            if not os.path.exists(original_path):
                self.stdout.write(f"⚠️  Image introuvable: {original_path}")
                return
            
            self.processed += 1
            
            # Vérifier la taille actuelle
            with Image.open(original_path) as img:
                original_size = os.path.getsize(original_path)
                original_width, original_height = img.size
                
                needs_resize = original_width > self.max_width
                webp_path = os.path.splitext(original_path)[0] + '.webp'
                needs_webp = not os.path.exists(webp_path)
                
                if not needs_resize and not needs_webp:
                    return
                
                optimizations = []
                
                # Redimensionner si nécessaire
                if needs_resize and not self.dry_run:
                    ratio = self.max_width / original_width
                    new_height = int(original_height * ratio)
                    
                    img_resized = img.copy()
                    img_resized.thumbnail((self.max_width, new_height), Image.Resampling.LANCZOS)
                    img_resized.save(original_path, optimize=True, quality=90)
                    
                    optimizations.append(f"redimensionné {original_width}x{original_height} → {self.max_width}x{new_height}")
                
                # Convertir en WebP
                if needs_webp:
                    if not self.dry_run:
                        webp_path = convert_to_webp(original_path, self.quality)
                        if webp_path != original_path:
                            webp_size = os.path.getsize(webp_path)
                            compression_ratio = (1 - webp_size / original_size) * 100
                            optimizations.append(f"WebP créé (-{compression_ratio:.1f}%)")
                    else:
                        optimizations.append("WebP à créer")
                
                if optimizations:
                    self.optimized += 1
                    optimization_text = ", ".join(optimizations)
                    
                    if self.dry_run:
                        self.stdout.write(f"   🔍 {context}: {optimization_text}")
                    else:
                        self.stdout.write(f"   ✅ {context}: {optimization_text}")
                        
        except Exception as e:
            self.stdout.write(f"   ❌ Erreur lors du traitement de {image_field.name}: {e}")
            self.errors += 1

    def display_summary(self):
        """Affiche le résumé des optimisations"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ DES OPTIMISATIONS'))
        self.stdout.write('='*50)
        
        self.stdout.write(f"📈 Images traitées: {self.processed}")
        self.stdout.write(f"✅ Images optimisées: {self.optimized}")
        self.stdout.write(f"❌ Erreurs: {self.errors}")
        
        if self.processed > 0:
            success_rate = (self.optimized / self.processed) * 100
            self.stdout.write(f"🎯 Taux de réussite: {success_rate:.1f}%")
        
        if self.dry_run:
            self.stdout.write(f"\n🔧 Pour appliquer les optimisations, relancez sans --dry-run")
        elif self.optimized > 0:
            self.stdout.write(f"\n🚀 Optimisations terminées ! Votre site devrait être plus rapide.")
            self.stdout.write(f"💡 N'oubliez pas de tester les images optimisées sur votre site.")
        
        # Recommandations
        if self.errors > 0:
            self.stdout.write(f"\n⚠️  {self.errors} erreur(s) détectée(s). Vérifiez les logs pour plus de détails.")
        
        if self.optimized == 0 and self.processed > 0:
            self.stdout.write(f"\n✨ Toutes vos images sont déjà optimisées !")