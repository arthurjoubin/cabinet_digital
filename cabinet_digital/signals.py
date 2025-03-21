from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from django.conf import settings
from PIL import Image
import os
from io import BytesIO
from .models import UserProfile, ReviewImage
import uuid
import random
import string


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