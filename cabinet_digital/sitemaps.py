from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Software, SoftwareCategory, Actualites, AIModel, AITool, AIArticle, Metier
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

class StaticViewSitemap(BaseSitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home', 'contact', 'outils']

    def location(self, item):
        return reverse(item)

class AIModelSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return AIModel.objects.filter(is_published=True).order_by('name')

    def location(self, obj):
        return reverse('ai_model_detail', kwargs={'slug': obj.slug})

class AIToolSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return AITool.objects.filter(is_published=True).order_by('name')

    def location(self, obj):
        return reverse('ai_tool_detail', kwargs={'slug': obj.slug})

class AIArticleSitemap(BaseSitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return AIArticle.objects.filter(is_published=True).order_by('-pub_date')

    def lastmod(self, obj):
        return obj.pub_date

    def location(self, obj):
        return reverse('ai_article_detail', kwargs={'slug': obj.slug})

class MetierSitemap(BaseSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Metier.objects.all().order_by('name')

    def lastmod(self, obj):
        return None

    def location(self, obj):
        return reverse('metier_detail', kwargs={'slug': obj.slug}) 