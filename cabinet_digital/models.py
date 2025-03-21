from django.db import models
from django.utils import timezone
from django.urls import reverse
from tinymce.models import HTMLField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.conf import settings

class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100)
    description = HTMLField(blank=True)
    slug = models.SlugField(blank=True, unique=False)
    metier = models.ForeignKey('Metier', on_delete=models.CASCADE, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    icon = models.FileField(upload_to='icons/', null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    excerpt = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Logiciels - Catégories"
        verbose_name_plural = "Logiciels - Catégories"

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=False, blank=True)
    color = models.CharField(max_length=50, blank=True)
    class Meta:
        verbose_name = "Logiciels - Tags"
        verbose_name_plural = "Logiciels - Tags"
    def __str__(self):
        return self.name
    

class Software(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = HTMLField()
    excerpt = models.CharField(max_length=200, blank=True)
    category = models.ManyToManyField('SoftwareCategory', related_name='categories_softwares_link')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    image_principale = models.ImageField(upload_to='images/',null=True, blank=True)
    site = models.URLField(max_length=200, blank=True)
    video = models.URLField(max_length=1000, blank=True)
    is_top_pick = models.BooleanField(default=False)
    unique_views = models.IntegerField(default=0)
    metier = models.ForeignKey('Metier', on_delete=models.CASCADE, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    preview_gif = models.ImageField(upload_to='software_previews/', null=True, blank=True)

    def clean(self):
        super().clean()
        if self.video:
            try:
                URLValidator()(self.video)
            except ValidationError:
                raise ValidationError({'video': 'Entrez une URL valide.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-is_top_pick', 'name']
        verbose_name = "Logiciel - Liste"
        verbose_name_plural = "Logiciels - Liste"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('software_detail', kwargs={'slug': self.slug})
        
    def average_rating(self):
        """Get the average rating for this software"""
        reviews = self.reviews.filter(status='published')
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return None
        
    def review_count(self):
        """Get the number of published reviews for this software"""
        return self.reviews.filter(status='published').count()
        
    def get_star_rating(self):
        """Get the rating as a string of stars"""
        avg = self.average_rating()
        if avg is None:
            return ""
        
        # Round to nearest half
        avg = round(avg * 2) / 2
        
        # Convert to stars
        full_stars = int(avg)
        half_star = avg - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        return "★" * full_stars + ("½" if half_star else "") + "☆" * int(empty_stars)

class Actualites(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    pub_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Logiciels - Actualités"


class Metier(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    seo_title = models.CharField(max_length=60, blank=True, help_text="Titre optimisé pour le référencement (60 caractères max)")
    seo_description = models.CharField(max_length=160, blank=True, help_text="Description optimisée pour le référencement (160 caractères max)")
    
    class Meta:
        verbose_name = "Logiciels - Métiers"
        verbose_name_plural = "Logiciels - Métiers"


    def __str__(self):
        return self.name

class ProviderAI(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = HTMLField(blank=True)
    logo = models.ImageField(upload_to='providers/', null=True, blank=True)
    site = models.URLField(max_length=200, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "IA - Editeurs"
        verbose_name_plural = "IA - Editeurs"


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('provider_detail', kwargs={'slug': self.slug})

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    provider = models.ForeignKey(ProviderAI, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = HTMLField()
    excerpt = models.CharField(max_length=200, blank=True)
    price = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    site = models.URLField(max_length=200, blank=True)

    is_top_pick = models.BooleanField(default=False)
    unique_views = models.IntegerField(default=0)
    tags = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "IA - Modèle"
        verbose_name_plural = "IA - Modèles"


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ai_model_detail', kwargs={'slug': self.slug})

class AIToolCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = HTMLField()
    excerpt = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "IA - Catégories"
        verbose_name_plural = "IA - Catégories"


class AITool(models.Model):
    provider = models.ForeignKey(ProviderAI, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = HTMLField()
    excerpt = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_top_pick = models.BooleanField(default=False)
    unique_views = models.IntegerField(default=0)
    site = models.URLField(max_length=200, blank=True)
    category = models.ManyToManyField(AIToolCategory, blank=True)

    class Meta:
        verbose_name = "IA - Outil"
        verbose_name_plural = "IA - Outils"


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ai_tool_detail', kwargs={'slug': self.slug})
    



class AIArticle(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.CharField(max_length=500)
    content = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True)
    banner = models.ImageField(upload_to='articles/images', null=True, blank=True)
    is_published = models.BooleanField(default=True)
    banner = models.ImageField(upload_to='articles/banners', null=True, blank=True)
    related_ai_models = models.ManyToManyField(AIModel, blank=True)
    related_ai_tools = models.ManyToManyField(AITool, blank=True)
    tags = models.CharField(max_length=50, blank=True)
    site = models.URLField(max_length=200, blank=True)

    class Meta:
        verbose_name = "IA - Article"
        verbose_name_plural = "IA - Articles"


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ai_article_detail', kwargs={'slug': self.slug})

class UserProfile(models.Model):
    """
    User profile model extending the default User model
    Stores additional user information for the review system
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile')
    username = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"


class Review(models.Model):
    """
    Review model for software products
    """
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('pending', 'En attente de validation'),
        ('rejected', 'Rejeté'),
        ('published', 'Publié'),
    )
    
    RATING_CHOICES = (
        (1, '1 - Très mauvais'),
        (2, '2 - Mauvais'),
        (3, '3 - Moyen'),
        (4, '4 - Bon'),
        (5, '5 - Excellent'),
    )
    
    software = models.ForeignKey(Software, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_reason = models.TextField(blank=True, null=True, help_text="Raison du rejet (visible uniquement par l'utilisateur)")
    publish_date = models.DateTimeField(null=True, blank=True, help_text="Date de publication")
    
    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-publish_date', '-created_at']
        unique_together = ['user', 'software']
    
    def __str__(self):
        return f"{self.user.userprofile.username} - {self.software.name} - {self.get_rating_display()}"
    
    def save(self, *args, **kwargs):
        # If review is being published for the first time, set publish date
        if self.status == 'published' and not self.publish_date:
            self.publish_date = timezone.now()
        super().save(*args, **kwargs)
    
    def can_be_edited(self):
        """Check if the review can still be edited (within 24h window)"""
        if not self.publish_date:
            return True
        edit_window = timezone.now() - timezone.timedelta(hours=settings.REVIEW_EDIT_WINDOW_HOURS)
        return self.publish_date > edit_window
    
    def upvotes(self):
        return self.votes.filter(vote=1).count()
    
    def downvotes(self):
        return self.votes.filter(vote=-1).count()
    
    def vote_score(self):
        return self.upvotes() - self.downvotes()


class ReviewImage(models.Model):
    """
    Images for reviews
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/', null=True, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Image d'avis"
        verbose_name_plural = "Images d'avis"


class ReviewVote(models.Model):
    """
    Votes on reviews (upvote/downvote)
    """
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_votes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Vote d'avis"
        verbose_name_plural = "Votes d'avis"
        unique_together = ['user', 'review']
        
    def __str__(self):
        return f"{self.user.userprofile.username} - {'👍' if self.vote == 1 else '👎'} - {self.review.software.name}"
