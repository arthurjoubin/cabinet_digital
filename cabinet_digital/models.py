from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.conf import settings
from django.core.cache import cache
import uuid
from django.utils.text import slugify
from .managers import PublishedManager

class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
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
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color = models.CharField(max_length=50, blank=True)
    seo_title = models.CharField(max_length=200, blank=True, help_text="Titre SEO pour la page du tag")
    seo_description = models.TextField(max_length=300, blank=True, help_text="Description SEO pour la page du tag")
    seo_content = models.TextField(blank=True, help_text="Contenu SEO affiché en haut de la page du tag")
    is_published = models.BooleanField(default=True, help_text="Contrôle la visibilité de la page du tag")
    
    class Meta:
        verbose_name = "Logiciels - Tags"
        verbose_name_plural = "Logiciels - Tags"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})

class Company(models.Model):
    """
    Represents a company that can be a software editor, PDP provider, or both
    """
    name = models.CharField(max_length=255, verbose_name="Nom")
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name="Logo")
    description = models.TextField(blank=True, verbose_name="Description")
    excerpt = models.CharField(max_length=300, blank=True, verbose_name="Extrait")
    website = models.URLField(blank=True, verbose_name="Site web")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Entreprise / Éditeur"
        verbose_name_plural = "Entreprises / Éditeurs"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('company_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Software(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    excerpt = models.CharField(max_length=200, blank=True)
    category = models.ManyToManyField('SoftwareCategory', related_name='categories_softwares_link')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    site = models.URLField(max_length=200, blank=True)
    is_top_pick = models.BooleanField(default=False)
    metier = models.ForeignKey('Metier', on_delete=models.CASCADE, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    # Add company as editor
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='software_products', verbose_name="Éditeur")

    objects = models.Manager()
    published = PublishedManager()

    def clean(self):
        super().clean()

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
    # Add company to link articles to companies
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='articles', verbose_name="Éditeur lié")

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
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='providers/', null=True, blank=True)
    site = models.URLField(max_length=200, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "IA - Editeurs"
        verbose_name_plural = "IA - Editeurs"


    def __str__(self):
        return self.name

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    provider = models.ForeignKey(ProviderAI, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    excerpt = models.CharField(max_length=200, blank=True)
    price = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    site = models.URLField(max_length=200, blank=True)

    is_top_pick = models.BooleanField(default=False)
    tags = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "IA - Modèle"
        verbose_name_plural = "IA - Modèles"


    def __str__(self):
        return self.name

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
    tags = models.CharField(max_length=50, blank=True)
    site = models.URLField(max_length=200, blank=True)

    class Meta:
        verbose_name = "IA - Article"
        verbose_name_plural = "IA - Articles"


    def __str__(self):
        return self.title



class Integrator(models.Model):
    """Represents service providers that implement software solutions"""
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='integrators/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_top_pick = models.BooleanField(default=False)
    site = models.URLField(max_length=200, blank=True)
    softwares = models.ManyToManyField(Software, blank=True, related_name='integrators')
    tags = models.CharField(max_length=500, blank=True, help_text="Tags séparés par des virgules")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Intégrateur"
        verbose_name_plural = "Intégrateurs"
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('integrator_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []



class PDPSpecialtyTag(models.Model):
    """
    Tag model for PDP specialties with SEO capabilities
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    is_published = models.BooleanField(default=True, help_text="Contrôle la visibilité de la page du tag", verbose_name="Publié")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "PDP - Tag de spécialité"
        verbose_name_plural = "PDP - Tags de spécialité"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('pdp_specialty_detail', kwargs={'slug': self.slug})
    
    def get_pdp_count(self):
        """Get count of PDPs that have this specialty"""
        return PlatformeDematerialisation.objects.filter(
            specialty__icontains=self.name,
            is_published=True
        ).count()

class PlatformeDematerialisation(models.Model):
    """
    Plateforme de Dématérialisation Partenaire (PDP) model
    """
    name = models.CharField(max_length=255, verbose_name="Nom")
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='pdp_logos/', blank=True, null=True)
    excerpt = models.TextField(verbose_name="Description", help_text="Description de la plateforme")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='pdp_platforms', verbose_name="Éditeur")
    specialty = models.CharField(max_length=100, verbose_name="Spécialité", blank=True, help_text="Spécialité ou domaine d'expertise principal")
    site = models.URLField(verbose_name="Site web", blank=True)
    integrators = models.ManyToManyField(Integrator, related_name='pdp_platforms', blank=True, verbose_name="Intégrateurs")
    connected_softwares = models.ManyToManyField(Software, related_name='pdp_platforms', blank=True, verbose_name="Solutions connectées")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pdp_detail', kwargs={'slug': self.slug})

    def get_specialty_tags_list(self):
        """Return specialty tags as a list"""
        if self.specialty:
            return [tag.strip() for tag in self.specialty.split(',') if tag.strip()]
        return []

    def get_specialty_tags_as_objects(self):
        """Return specialty tags as PDPSpecialtyTag objects if they exist"""
        tags_list = self.get_specialty_tags_list()
        specialty_objects = []
        
        for tag_name in tags_list:
            try:
                tag_obj = PDPSpecialtyTag.objects.get(name__iexact=tag_name, is_published=True)
                specialty_objects.append(tag_obj)
            except PDPSpecialtyTag.DoesNotExist:
                # Create a simple object with name and slug for tags that don't have a PDPSpecialtyTag
                from types import SimpleNamespace
                tag_obj = SimpleNamespace()
                tag_obj.name = tag_name
                tag_obj.slug = slugify(tag_name)
                specialty_objects.append(tag_obj)
        
        return specialty_objects

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Plateforme de Dématérialisation"
        verbose_name_plural = "Plateformes de Dématérialisation"
        ordering = ['name']


class Contact(models.Model):
    """Modèle pour les messages de contact"""
    nom = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    entreprise = models.CharField(max_length=200, verbose_name="Entreprise")
    message = models.TextField(verbose_name="Message")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    traite = models.BooleanField(default=False, verbose_name="Traité")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.email} - {self.date_creation.strftime('%d/%m/%Y')}"


# Integration models (merged from integrations app)

class TypeIntegration(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = "Type d'intégration"
        verbose_name_plural = "Types d'intégration"
        ordering = ['nom']
        db_table = 'integrations_typeintegration'
    
    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Module(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône (ex: file-text, calculator, etc.)")
    ordre = models.IntegerField(default=0, help_text="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ['ordre', 'nom']
        db_table = 'integrations_module'
    
    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)





class Integration(models.Model):
    nom = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    logiciel_source = models.ForeignKey('Software', on_delete=models.CASCADE, related_name='integrations_source', verbose_name="Logiciel source")
    logiciel_destination = models.ForeignKey('Software', on_delete=models.CASCADE, related_name='integrations_destination', verbose_name="Logiciel destination")
    integrateur = models.ForeignKey(Integrator, on_delete=models.CASCADE, related_name='integrations')
    type_integration = models.ForeignKey(TypeIntegration, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Type d'intégration")
    modules = models.ManyToManyField(Module, blank=True, verbose_name="Modules concernés", help_text="Modules comptables concernés par cette intégration", db_table='integrations_integration_modules')
    description = models.TextField()
    fonctionnalites = models.TextField(help_text="Liste des fonctionnalités, une par ligne", blank=True)
    prix = models.CharField(max_length=200, blank=True, help_text="Ex: À partir de 50€/mois")
    url_documentation = models.URLField(blank=True, verbose_name="URL de documentation")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Intégration"
        verbose_name_plural = "Intégrations"
        ordering = ['-date_creation']
        unique_together = ['logiciel_source', 'logiciel_destination', 'integrateur']
        db_table = 'integrations_integration'
    
    def __str__(self):
        return f"{self.logiciel_source.name} → {self.logiciel_destination.name} ({self.integrateur.name})"
    
    def get_absolute_url(self):
        return reverse('integration_detail', kwargs={'slug': self.slug})
    
    def get_fonctionnalites_list(self):
        if not self.fonctionnalites:
            return []
        return [f.strip() for f in self.fonctionnalites.split('\n') if f.strip()]

    def save(self, *args, **kwargs):
        if not self.slug:
            # Génère automatiquement le nom et le slug si non fournis
            if not self.nom:
                self.nom = f"{self.logiciel_source.name} vers {self.logiciel_destination.name}"
            self.slug = slugify(f"{self.logiciel_source.slug}-vers-{self.logiciel_destination.slug}-{self.integrateur.slug}")
        super().save(*args, **kwargs)


class ContactIntegrateur(models.Model):
    TYPES_CONTACT = [
        ('integrateur', 'Intégrateur'),
        ('editeur', 'Éditeur de logiciel'),
        ('autre', 'Autre'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    entreprise = models.CharField(max_length=200, verbose_name="Entreprise")
    type_contact = models.CharField(max_length=20, choices=TYPES_CONTACT, verbose_name="Type de contact")
    logiciel_source = models.CharField(max_length=200, verbose_name="Logiciel source", help_text="Nom du logiciel source de l'intégration")
    logiciel_destination = models.CharField(max_length=200, verbose_name="Logiciel destination", help_text="Nom du logiciel destination de l'intégration")
    modules_concernes = models.TextField(verbose_name="Modules concernés", help_text="Quels modules comptables sont concernés par cette intégration ?")
    description = models.TextField(verbose_name="Description de l'intégration", help_text="Décrivez votre intégration en détail")
    url_documentation = models.URLField(blank=True, verbose_name="URL de documentation", help_text="Lien vers la documentation technique (optionnel)")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone (optionnel)")
    date_creation = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False, verbose_name="Traité")
    
    class Meta:
        verbose_name = "Contact intégrateur"
        verbose_name_plural = "Contacts intégrateurs"
        ordering = ['-date_creation']
        db_table = 'integrations_contactintegrateur'
    
    def __str__(self):
        return f"{self.nom} - {self.logiciel_source} → {self.logiciel_destination}"


class ContactIntegrator(models.Model):
    """Contact form for integrators (companies) wanting to be listed"""
    
    nom = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    entreprise = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    site_web = models.URLField(verbose_name="Site web", blank=True)
    description = models.TextField(verbose_name="Description de votre activité")
    logiciels_expertise = models.TextField(verbose_name="Logiciels d'expertise", help_text="Quels logiciels maîtrisez-vous ?")
    zone_intervention = models.CharField(max_length=200, verbose_name="Zone d'intervention", help_text="Région, département, national...")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    traite = models.BooleanField(default=False, verbose_name="Traité")
    
    class Meta:
        verbose_name = "Contact intégrateur entreprise"
        verbose_name_plural = "Contacts intégrateurs entreprises"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} - {self.entreprise}"
