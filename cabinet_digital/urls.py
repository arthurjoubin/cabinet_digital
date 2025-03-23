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
from cabinet_digital.views import (
    CategoryListView, CategoryDetailView, ActualitesListView, ActualitesDetailView,
    alternative_detail, SoftwareDetailView, SoftwareListView, Custom404View,
    AIModelListView, AIModelDetailView, AIToolListView, AIToolDetailView,
    AIArticleListView, AIArticleDetailView, ProviderDetailView,
    CompleteProfileView, UserProfileView, UserReviewsView, ReviewCreateView, 
    ReviewEditView, ReviewDeleteView, ReviewVoteView,
    ToggleSoftwareSelectionView, UserSoftwareCollectionListView
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import redirect
from django.utils.text import slugify
import unidecode
from cabinet_digital.sitemaps import (
    SoftwareSitemap, CategorySitemap, ActualitesSitemap, StaticViewSitemap,
    AIModelSitemap, AIToolSitemap, AIArticleSitemap, MetierSitemap
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
    'static': StaticViewSitemap,
    'ai_models': AIModelSitemap,
    'ai_tools': AIToolSitemap,
    'ai_articles': AIArticleSitemap,
    'metiers': MetierSitemap,
}

# Modifiez ces lignes au début du fichier
admin.site.site_header = "Cabinet Digital"
admin.site.site_title = "Cabinet Digital Admin Portal"
admin.site.index_title = "Bienvenue sur Cabinet Digital"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logiciels/', SoftwareListView.as_view(), name='software_list'),
    path('', views.home, name='home'),
    path('logiciels/<str:slug>/', SoftwareDetailView.as_view(), name='software_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('metiers/<slug:slug>/', views.MetierDetailView.as_view(), name='metier_detail'),
    path('contact/', views.contact, name='contact'),
    path('actualites/', views.actualites, name='actualites'),
    path('actualites/<slug:slug>/', ActualitesDetailView.as_view(), name='actualite_detail'),
    path('logiciels/<str:slug>/alternatives/', alternative_detail, name='alternative_detail'),
    
    # Debug URLs
    path('debug/email-test/', views.debug_email_test, name='debug_email_test'),
    
    # Authentication URLs
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/complete/', CompleteProfileView.as_view(), name='complete_profile'),
    path('accounts/profile/', UserProfileView.as_view(), name='user_profile'),
    path('accounts/profile/reviews/', UserReviewsView.as_view(), name='user_reviews'),
    path('post-social-login/', views.post_social_login, name='post_social_login'),
    
    # Review URLs
    path('logiciels/<str:slug>/review/create/', ReviewCreateView.as_view(), name='review_create'),
    path('logiciels/<str:slug>/review/<int:pk>/edit/', ReviewEditView.as_view(), name='review_edit'),
    path('logiciels/<str:slug>/review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),
    path('review/<int:pk>/vote/', ReviewVoteView.as_view(), name='review_vote'),
    
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
    path('outils/', views.outils, name='outils'),
    
    # URLs pour les sélections de logiciels
    path('software/selection/toggle/', ToggleSoftwareSelectionView.as_view(), name='toggle_software_selection'),
    path('mes_logiciels/', UserSoftwareCollectionListView.as_view(), name='mes_logiciels'),
    
    path('ia/modeles/', AIModelListView.as_view(), name='ai_model_list'),
    path('ia/modeles/<slug:slug>/', AIModelDetailView.as_view(), name='ai_model_detail'),
    path('ia/editeurs/<slug:slug>/', ProviderDetailView.as_view(), name='provider_detail'),
    path('ia/outils/', AIToolListView.as_view(), name='ai_tool_list'),
    path('ia/outils/<slug:slug>/', AIToolDetailView.as_view(), name='ai_tool_detail'),
    path('ia/guides/', AIArticleListView.as_view(), name='ai_article_list'),
    path('ia/guides/<slug:slug>/', AIArticleDetailView.as_view(), name='ai_article_detail'),
]

urlpatterns += [
    path('404/', views.Custom404View.as_view(), name='404'),
]
handler404 = 'cabinet_digital.views.custom_404_view'
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

