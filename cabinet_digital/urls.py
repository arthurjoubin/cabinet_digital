"""
URL configuration for cabinet_digital project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from cabinet_digital import views
from cabinet_digital.views import ArticleListView, ArticleDetailView, CategoryListView, CategoryDetailView, NewsListView, NewsDetailView, alternative_detail, SoftwareDetailView, SoftwareListView, Custom404View
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from .sitemaps import sitemaps
from django.shortcuts import redirect
from django.utils.text import slugify
import unidecode

def custom_redirect(request, slug, any_value, target_path):
    # Supprimer les accents avant d'appliquer slugify
    unaccented_slug = unidecode.unidecode(slug)
    # Appliquer slugify sur le slug sans accent
    new_slug = slugify(unaccented_slug)
    # Construire l'URL de redirection
    redirect_url = f'/{target_path}/{new_slug}/'
    return redirect(redirect_url, permanent=True)

urlpatterns = [

    path('admin/', admin.site.urls),
    path('logiciels/',  views.SoftwareListView.as_view(), name='software_list'),
    path('', views.home, name='home'),
    path('logiciels/<str:slug>/', SoftwareDetailView.as_view(), name='software_detail'),
    re_path(r'^solution/(?P<slug>[\w-]+[^/]+)/r/(?P<any_value>.+)$', views.custom_redirect_view, {'target_path': 'logiciels'}, name='solution_redirect'),
    re_path(r'^news/(?P<slug>[\w-]+[^/]+)/r/(?P<any_value>.+)$', views.custom_redirect_view, {'target_path': 'actualites'}, name='news_redirect'),
    re_path(r'^article/(?P<slug>[\w-]+[^/]+)/r/(?P<any_value>.+)$', views.custom_redirect_view, {'target_path': 'articles'}, name='article_redirect'),
    re_path(r'^categorie/(?P<slug>[\w-]+[^/]+)/r/(?P<any_value>.+)$', views.custom_redirect_view, {'target_path': 'categories'}, name='category_redirect'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('articles/', ArticleListView.as_view(), name='articles'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('contact/', views.contact, name='contact'),
    path('actualites/', NewsListView.as_view(), name='news_list'),
    path('actualites/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('markdownx/', include('markdownx.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('logiciels/<str:slug>/alternatives/', alternative_detail, name='alternative_detail'),
    path('sitemap.xml', sitemap_index, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.index'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('ai-text-processor/', views.ai_text_processor, name='ai_text_processor'),
    re_path(r'^(?P<old_path>solution|news|article|categorie)/(?P<slug>.*)/r/(?P<any_value>.*)$', views.custom_redirect_view, name='custom_redirect')]

if settings.DEBUG:
    urlpatterns += [
        path('404/', views.Custom404View.as_view(), name='404'),
    ]
handler404 = 'cabinet_digital.views.custom_404_view'

# Servir les fichiers média en production et en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
