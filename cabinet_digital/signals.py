from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.conf import settings
from PIL import Image
import os
from io import BytesIO
from .models import UserProfile, ReviewImage, Review, SoftwareCategory, Software
import uuid
import random
import string
import logging
from django.core.cache import cache

logger = logging.getLogger('cabinet_digital')


@receiver(user_signed_up)
def create_user_profile(sender, request, user, **kwargs):
    """Create a UserProfile instance for newly registered users"""
    # Create temporary username from email
    email_username = user.email.split('@')[0]
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    temp_username = f"{email_username}_{random_suffix}"
    
    # Create profile with temporary username
    UserProfile.objects.create(
        user=user,
        username=temp_username
    )


@receiver(pre_save, sender=ReviewImage)
def process_review_image(sender, instance, **kwargs):
    """Process review images before saving"""
    if instance.image and hasattr(instance.image, 'file'):
        # Check file MIME type for security
        try:
            import magic
            file_mime = magic.from_buffer(instance.image.read(1024), mime=True)
            instance.image.seek(0)  # Reset file pointer
            
            allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if file_mime not in allowed_types:
                from django.core.exceptions import ValidationError
                raise ValidationError('Type de fichier non autorisé. Seuls les images JPEG, PNG, WebP et GIF sont acceptées.')
        except ImportError:
            logger.warning("python-magic not installed, skipping MIME type validation")
        
        # Generate new filename with uuid to avoid collisions
        img = Image.open(instance.image)
        
        # Convert to WebP
        webp_io = BytesIO()
        
        # Resize image if larger than max dimensions
        max_size = settings.REVIEW_IMAGE_MAX_SIZE
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size)
        
        # Save as WebP
        img.save(webp_io, 'WEBP', quality=settings.REVIEW_IMAGE_QUALITY)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.webp"
        
        # Save the new image
        from django.core.files.base import ContentFile
        instance.image.save(
            filename,
            ContentFile(webp_io.getvalue()),
            save=False  # Don't save yet to avoid recursion
        )


@receiver(post_save, sender=Review)
def notify_on_review_creation(sender, instance, created, **kwargs):
    """Envoie une notification quand un nouvel avis est créé"""
    logger.info(f"Signal triggered for review - created: {created}")
    if created:  # Seulement pour les nouveaux avis, pas les mises à jour
        logger.info(f"New review detected, sending notification for review #{instance.id}")
        from cabinet_digital.utils import send_new_review_notification
        send_new_review_notification(instance)
    
    # Invalidate caches related to software
    cache.delete(f'software_{instance.software.id}_avg_rating')
    cache.delete(f'software_{instance.software.id}_review_count')
    cache.delete(f'software_card_{instance.software.id}')  # Invalider le cache de la carte

@receiver([post_save, post_delete], sender=SoftwareCategory)
def invalidate_category_cache(sender, instance, **kwargs):
    """Invalidate category cache when a category is saved or deleted"""
    cache.delete('header_categories')
    
    # Invalider les cartes des logiciels associés à cette catégorie
    for software in instance.categories_softwares_link.all():
        cache.delete(f'software_card_{software.id}')

@receiver([post_save, post_delete], sender=Software)
def invalidate_software_related_caches(sender, instance, **kwargs):
    """Invalidate related caches when a software is saved or deleted"""
    cache.delete('header_categories')  # Because software count might change
    
    # Invalidate rating caches
    cache.delete(f'software_{instance.id}_avg_rating')
    cache.delete(f'software_{instance.id}_review_count')
    cache.delete(f'software_card_{instance.id}')  # Invalider le cache de la carte

@receiver(post_delete, sender=Review)
def invalidate_review_caches(sender, instance, **kwargs):
    """Invalidate caches related to software when a review is deleted"""
    # Invalidate caches related to software
    if hasattr(instance, 'software') and instance.software:
        cache.delete(f'software_{instance.software.id}_avg_rating')
        cache.delete(f'software_{instance.software.id}_review_count')
        cache.delete(f'software_card_{instance.software.id}')  # Invalider le cache de la carte 