from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import SoftwareCategory, Software, Article, Actualites
from django.utils import timezone

class StaticViewSitemap(Sitemap):
    def items(self):
        return ['home', 'category_list', 'software_list', 'about', 'contact']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()

class CategorySitemap(Sitemap):
    def items(self):
        return SoftwareCategory.objects.all()

    def lastmod(self, obj):
        return obj.last_modified

class SoftwareSitemap(Sitemap):
    def items(self):
        return Software.objects.all()

    def lastmod(self, obj):
        return obj.last_modified

class ArticleSitemap(Sitemap):
    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.pub_date

class ActualitesSitemap(Sitemap):
    def items(self):
        return Actualites.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.date

sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'softwares': SoftwareSitemap,
    'articles': ArticleSitemap,
    'actualites': ActualitesSitemap,
}