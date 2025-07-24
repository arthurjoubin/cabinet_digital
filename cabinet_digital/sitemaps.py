from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import (Software, SoftwareCategory, Actualites, 
                     Metier, Tag, PlatformeDematerialisation, PDPSpecialtyTag, Integrator)
from django.contrib.sites.shortcuts import get_current_site

class BaseSitemap(Sitemap):
    protocol = 'https'

    def get_site(self, site=None):
        site = super().get_site(site)
        site.domain = f'www.{site.domain}'
        return site

class SoftwareSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Software.objects.filter(is_published=True).order_by('name')

    def lastmod(self, obj):
        return obj.last_modified

    def location(self, obj):
        return reverse('software_detail', kwargs={'slug': obj.slug})

class SoftwareIntegratorsSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Software.objects.filter(
            is_published=True,
            integrators__isnull=False
        ).distinct().order_by('name')

    def lastmod(self, obj):
        return obj.last_modified

    def location(self, obj):
        return reverse('software_integrators_seo', kwargs={'slug': obj.slug})

class CategorySitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return SoftwareCategory.objects.filter(is_published=True).order_by('name')

    def lastmod(self, obj):
        return obj.last_modified

    def location(self, obj):
        return reverse('category_detail', kwargs={'slug': obj.slug})

class ActualitesSitemap(BaseSitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Actualites.objects.filter(is_published=True).order_by('-pub_date')

    def lastmod(self, obj):
        return obj.pub_date

    def location(self, obj):
        return reverse('actualite_detail', kwargs={'slug': obj.slug})

class TagSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # Inclure uniquement les tags publiés qui ont au moins une actualité publiée
        return Tag.objects.filter(
            is_published=True,
            actualites__is_published=True
        ).distinct().order_by('name')

    def location(self, obj):
        return reverse('tag_detail', kwargs={'slug': obj.slug})

class PDPSpecialtyTagSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        # Inclure uniquement les tags de spécialité publiés qui ont au moins une PDP
        return PDPSpecialtyTag.objects.filter(
            is_published=True
        ).order_by('name')

    def location(self, obj):
        return reverse('pdp_specialty_detail', kwargs={'slug': obj.slug})
    
    def lastmod(self, obj):
        return obj.updated_at

class PlatformeDematerialisationSitemap(BaseSitemap):
    """
    Sitemap pour les pages individuelles des PDP
    Priorité élevée car contenu spécialisé et à forte valeur ajoutée
    """
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PlatformeDematerialisation.objects.filter(is_published=True).order_by('name')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('pdp_detail', kwargs={'slug': obj.slug})

class PDPListSitemap(BaseSitemap):
    """
    Sitemap pour la page de liste des PDP
    Optimisé pour "La liste à jour des XX PDP accrédités"
    """
    changefreq = "daily"  # Mise à jour fréquente car liste dynamique
    priority = 0.9  # Priorité très élevée pour la page principale

    def items(self):
        # Retourne un seul élément pour la page de liste
        return ['pdp_list']

    def location(self, item):
        return reverse('pdp_list')

    def lastmod(self, obj):
        # Dernière modification basée sur la PDP la plus récemment mise à jour
        latest_pdp = PlatformeDematerialisation.objects.filter(
            is_published=True
        ).order_by('-updated_at').first()
        return latest_pdp.updated_at if latest_pdp else None

class PDPSpecialtyListSitemap(BaseSitemap):
    """
    Sitemap pour les pages de spécialités PDP
    Optimisé pour "PDP spécialisées en [domaine]"
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        # Récupérer toutes les spécialités uniques des PDP publiées
        specialty_fields = PlatformeDematerialisation.objects.filter(
            is_published=True
        ).exclude(
            specialty=''
        ).values_list('specialty', flat=True).distinct()
        
        # Extraire les tags individuels des champs spécialité séparés par virgules
        all_specialties = set()
        for specialty_field in specialty_fields:
            if specialty_field:
                tags = [tag.strip() for tag in specialty_field.split(',') if tag.strip()]
                all_specialties.update(tags)
        
        # Créer des objets avec slug pour chaque spécialité
        from django.utils.text import slugify
        specialty_objects = []
        for specialty in all_specialties:
            # Créer un objet simple avec les propriétés nécessaires
            from types import SimpleNamespace
            obj = SimpleNamespace()
            obj.name = specialty
            obj.slug = slugify(specialty)
            specialty_objects.append(obj)
        
        return specialty_objects

    def location(self, obj):
        return reverse('pdp_specialty_detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        # Dernière modification basée sur les PDP de cette spécialité
        latest_pdp = PlatformeDematerialisation.objects.filter(
            is_published=True,
            specialty__icontains=obj.name
        ).order_by('-updated_at').first()
        return latest_pdp.updated_at if latest_pdp else None

class StaticViewSitemap(BaseSitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home', 'contact', 'outils']

    def location(self, item):
        return reverse(item)

class MetierSitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Metier.objects.all().order_by('name')

    def lastmod(self, obj):
        return None

    def location(self, obj):
        return reverse('metier_detail', kwargs={'slug': obj.slug})

class IntegratorSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Integrator.objects.filter(is_published=True).order_by('name')

    def lastmod(self, obj):
        return None

    def location(self, obj):
        return reverse('integrator_detail', kwargs={'slug': obj.slug})

class SoftwareAlternativesSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # Include only published software that have alternatives (same categories)
        return Software.objects.filter(
            is_published=True,
            category__isnull=False
        ).distinct().order_by('name')

    def lastmod(self, obj):
        return obj.last_modified

    def location(self, obj):
        return reverse('alternative_detail', kwargs={'slug': obj.slug}) 