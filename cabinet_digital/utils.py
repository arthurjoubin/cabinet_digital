"""
Utilitaires pour l'optimisation des images et le SEO
"""
from PIL import Image
import os
from django.conf import settings
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)

def convert_to_webp(image_path, quality=85):
    """
    Convertit une image en format WebP pour optimiser les performances
    
    Args:
        image_path: Chemin vers l'image source
        quality: Qualité de compression (0-100)
    
    Returns:
        str: Chemin vers l'image WebP convertie
    """
    try:
        # Ouvrir l'image
        with Image.open(image_path) as img:
            # Convertir en RGB si nécessaire (pour les PNG avec transparence)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Créer un arrière-plan blanc pour les images transparentes
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Créer le chemin de destination WebP
            base_name = os.path.splitext(image_path)[0]
            webp_path = f"{base_name}.webp"
            
            # Sauvegarder en WebP
            img.save(webp_path, 'WebP', quality=quality, optimize=True)
            
            logger.info(f"Image convertie en WebP: {webp_path}")
            return webp_path
            
    except Exception as e:
        logger.error(f"Erreur lors de la conversion WebP de {image_path}: {e}")
        return image_path  # Retourner l'image originale en cas d'erreur

def get_optimized_image_url(image_field, format_preference=['webp', 'jpg', 'png']):
    """
    Retourne l'URL de l'image optimisée selon les formats supportés
    
    Args:
        image_field: Champ image Django
        format_preference: Liste des formats par ordre de préférence
    
    Returns:
        str: URL de l'image optimisée
    """
    if not image_field:
        return None
    
    original_path = image_field.path
    original_url = image_field.url
    
    # Vérifier si une version WebP existe
    base_path = os.path.splitext(original_path)[0]
    webp_path = f"{base_path}.webp"
    
    if os.path.exists(webp_path):
        # Retourner l'URL WebP
        webp_url = original_url.replace(
            os.path.splitext(original_url)[1], 
            '.webp'
        )
        return webp_url
    
    return original_url

def generate_responsive_image_srcset(image_field, sizes=[400, 800, 1200]):
    """
    Génère un srcset pour des images responsives
    
    Args:
        image_field: Champ image Django
        sizes: Liste des tailles d'image à générer
    
    Returns:
        dict: Dictionnaire avec srcset et sizes
    """
    if not image_field:
        return {}
    
    try:
        original_path = image_field.path
        original_url = image_field.url
        
        with Image.open(original_path) as img:
            original_width = img.width
            srcset_parts = []
            
            for size in sizes:
                if size <= original_width:
                    # Générer le nom de fichier redimensionné
                    base_name, ext = os.path.splitext(original_path)
                    resized_path = f"{base_name}_{size}w{ext}"
                    
                    if not os.path.exists(resized_path):
                        # Redimensionner l'image
                        img_resized = img.copy()
                        img_resized.thumbnail((size, size * img.height // img.width), Image.Resampling.LANCZOS)
                        img_resized.save(resized_path, optimize=True, quality=85)
                    
                    # Ajouter au srcset
                    resized_url = original_url.replace(
                        os.path.basename(original_url),
                        os.path.basename(resized_path)
                    )
                    srcset_parts.append(f"{resized_url} {size}w")
            
            return {
                'srcset': ', '.join(srcset_parts),
                'sizes': '(max-width: 400px) 100vw, (max-width: 800px) 50vw, 33vw'
            }
            
    except Exception as e:
        logger.error(f"Erreur lors de la génération du srcset: {e}")
        return {}