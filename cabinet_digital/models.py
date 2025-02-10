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
