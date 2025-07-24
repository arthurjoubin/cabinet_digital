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
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from cabinet_digital import views
from cabinet_digital import integration_views
from cabinet_digital.views import (
    CategoryListView, CategoryDetailView, ActualitesListView, ActualitesDetailView,
    alternative_detail, SoftwareDetailView, SoftwareListView, Custom404View,
    IntegratorListView, IntegratorDetailView,
    PDPListView, PDPDetailView, PDPSpecialtyDetailView, TagDetailView
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import redirect
from django.utils.text import slugify
import unidecode
from cabinet_digital.sitemaps import (
    SoftwareSitemap, CategorySitemap, ActualitesSitemap, StaticViewSitemap,
    MetierSitemap, TagSitemap, PDPSpecialtyTagSitemap,
    SoftwareIntegratorsSitemap, IntegratorSitemap, SoftwareAlternativesSitemap,
    PlatformeDematerialisationSitemap, PDPListSitemap, PDPSpecialtyListSitemap
)
from django.views.generic import TemplateView

def custom_redirect(request, old_path, slug, r_id=None):
    # Supprimer les accents avant d'appliquer slugify
    unaccented_slug = unidecode.unidecode(slug)
    
    # Si c'est une catégorie et que le slug commence par "logiciel_"
    if old_path == "categorie" and unaccented_slug.startswith("logiciel_"):
        # Retirer le préfixe "logiciel_"
        unaccented_slug = unaccented_slug[9:]  # 9 est la longueur de "logiciel_"
    
    # Appliquer slugify sur le slug sans accent
    new_slug = slugify(unaccented_slug)
    
    # Définir le target_path en fonction du old_path
    path_mapping = {
        'solution': 'solutions',
        'news': 'actualites',
        'article': 'articles',
        'categorie': 'categories'
    }
    target_path = path_mapping.get(old_path, old_path)
    
    # Construire l'URL de redirection
    if r_id:
        redirect_url = f'/{target_path}/{new_slug}/'  # On ne conserve pas le /r/ID
    else:
        redirect_url = f'/{target_path}/{new_slug}/'
    
    return redirect(redirect_url, permanent=True)

# Ajouter cette configuration des sitemaps
sitemaps = {
    'software': SoftwareSitemap,
    'categories': CategorySitemap,
    'actualites': ActualitesSitemap,
    'tags': TagSitemap,
    'pdp_specialties': PDPSpecialtyTagSitemap,
    'pdp': PlatformeDematerialisationSitemap,
    'pdp_list': PDPListSitemap,
    'pdp_specialty_pages': PDPSpecialtyListSitemap,
    'static': StaticViewSitemap,
    'metiers': MetierSitemap,
    'software_integrators': SoftwareIntegratorsSitemap,
    'integrators': IntegratorSitemap,
    'software_alternatives': SoftwareAlternativesSitemap,
}

# Modifiez ces lignes au début du fichier
admin.site.site_header = "Cabinet Digital"
admin.site.site_title = "Cabinet Digital Admin Portal"
admin.site.index_title = "Bienvenue sur Cabinet Digital"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('logiciels/', SoftwareListView.as_view(), name='software_list'),
    path('', views.home, name='home'),
    
    path('logiciels/<str:slug>/', SoftwareDetailView.as_view(), name='software_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('metiers/<slug:slug>/', views.MetierDetailView.as_view(), name='metier_detail'),
    # Contact URLs - Standardized structure
    path('contact/', views.contact, name='contact'),
    path('contact/logiciel/', views.contact_software, name='contact_software'),
    path('contact/integrateur/', views.contact_integrator, name='contact_integrator'),
    path('contact/integration/', integration_views.contact_integration, name='contact_integration'),
    path('a-propos/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('actualites/', ActualitesListView.as_view(), name='actualites'),
    path('actualites/<slug:slug>/', ActualitesDetailView.as_view(), name='actualite_detail'),
    path('actualites/tag/<slug:slug>/', TagDetailView.as_view(), name='tag_detail'),
    path('logiciels/<str:slug>/alternatives/', alternative_detail, name='alternative_detail'),
    path('logiciels/<str:slug>/integrateurs/', views.software_integrators, name='software_integrators'),
    path('integrateurs-<str:slug>/', SoftwareDetailView.as_view(), name='software_integrators_seo'),
    
    # Integrators URLs
    path('integrateurs/', IntegratorListView.as_view(), name='integrator_list'),
    path('integrateurs/<str:slug>/', IntegratorDetailView.as_view(), name='integrator_detail'),
    
    # PDP URLs
    path('plateformes-dematerialisation/', PDPListView.as_view(), name='pdp_list'),
    path('plateformes-dematerialisation/<str:slug>/', PDPDetailView.as_view(), name='pdp_detail'),
    path('plateformes-dematerialisation/specialite/<str:slug>/', PDPSpecialtyDetailView.as_view(), name='pdp_specialty_detail'),
    
    
    re_path(r'^(?P<old_path>categorie)/logiciel_(?P<slug>[^/]+)(?:/r/(?P<r_id>[^/]+))?/?$', 
    views.custom_redirect_view, 
    name='custom_redirect'),
    re_path(r'^(?P<old_path>solution|news|article)/(?P<slug>[^/]+)(?:/r/(?P<r_id>[^/]+))?/?$', 
        views.custom_redirect_view, 
        name='custom_redirect'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    re_path(r'^sitemap\.xml/$', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('outils/simulateur-roi-logiciel/', views.roi_calculateur, name='roi_calculateur'),
    path('outils/investissement-immobilier-simulateur/', views.immobilier_calculateur, name='immobilier_calculateur'),
    path('outils/sftp-script-generateur/', views.sftp_generator, name='sftp_generator'),
    path('outils/tableau-amortissement-generateur/', views.amortissement_calculateur, name='amortissement_calculateur'),
    path('outils/tableau-amortissement-<str:loan_type>/', views.amortissement_calculateur, name='amortissement_calculateur_type'),
    path('outils/', views.outils, name='outils'),
    
    # Integrations URLs (merged from integrations app)
    path('integrations/', integration_views.integration_list, name='integration_list'),
    path('integrations/test-email/', integration_views.test_email, name='test_email'),
    path('integrations/integration/<slug:slug>/', integration_views.integration_detail, name='integration_detail'),
    path('integrations/integrateur/<slug:slug>/', integration_views.integrateur_detail, name='integrateur_detail'),
]

urlpatterns += [
    path('404/', views.Custom404View.as_view(), name='404'),
]
handler404 = 'cabinet_digital.views.custom_404_view'
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

