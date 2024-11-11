from django.shortcuts import render
from .models import Software, SoftwareCategory, Article, Actualites
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.views.generic import ListView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils.safestring import mark_safe
from django.db.models import Count  
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify
import unidecode
from urllib.parse import unquote
import os
from django.utils.html import escape
from django.db.models.functions import Lower

REDIRECTIONS = {
    ('article', 'meilleur-logiciel-gestion-financière', 'recWaFwovIysDlxQG'): '/categories/gestion_financiere/',
    ('article', 'guide-facture-electronique', 'recXxEZlXjyGr0lw3'): '/actualites/facture-electronique-guide-complet/',
    ('article', 'plateforme-signature-electronique-expert-comptable', 'rec6S8akyphoBOQsi'): '/categories/signature_electronique/',
    ('article', 'marketing-expert-comptable-booster-digital', 'recE2FjMqGeNywEuY'): '/categories/communication/',
    ('article', 'ged-expert-comptable', 'recSzblWftOMr3gcR'): '/categories/ged_cabinet/',
    ('article', 'gestion-interne-expert-comptable', 'recB14p8Dmh1dDDWW'): '/categories/gestion_interne/',
    ('article', 'portail-client-expert-comptable', 'recnmO8UOKoWDtw6n'): '/categories/portail_client/',
    ('article', 'liste_candidats_pdp_facture_electronique', 'rec2aRliZkqrBZ8HP'): '/actualites/lliste-des-pdp-accreditees-facture-electronique/',
    ('article', 'congres-de-l-ordre-experts-comptables-2023-guide-complet', 'rec0TrJ0pZJzkfmxL'): '/actualites/guide-du-congres-de-lordre-des-experts-comptables/',
}

class ArticleListView(ListView):
    model = Article
    template_name = "article_list.html"
    queryset = Article.objects.filter(is_published=True)

class ArticleDetailView(DetailView):
    model = Article
    template_name = "article_detail.html"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter à 49 caractères
        
        return get_object_or_404(queryset, slug=clean_slug, is_published=True)

def home(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')



class CategoryListView(ListView):
    model = SoftwareCategory
    template_name = 'category_list.html'
    context_object_name = 'categories'
    def get_queryset(self):
        return SoftwareCategory.objects.annotate(
            software_count=Count('categories_softwares_link')
        ).order_by('name').filter(software_count__gt=0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CategoryDetailView(DetailView):
    model = SoftwareCategory
    template_name = 'category_detail.html'
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter à 49 caractères
        
        # Chercher la catégorie avec le slug nettoyé
        return get_object_or_404(queryset, slug=clean_slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context['category'] = category
        context['count'] = Software.objects.filter(category=category).count()
        context['softwares'] = Software.objects.filter(category=category)
        return context

class SoftwareListView(ListView):
    model = Software
    template_name = 'software_list.html'
    context_object_name = 'softwares'
    paginate_by = 16

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SoftwareCategory.objects.annotate(
            software_count=Count('categories_softwares_link')
        ).order_by(Lower('name'))
        context['selected_category'] = self.request.GET.get('categorie')
        context['search_query'] = self.request.GET.get('search', '')
        return context
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-is_top_pick', Lower('name'))
        queryset = queryset.filter(is_published=True, slug__isnull=False).exclude(slug='')
        category = self.request.GET.get('categorie')
        search = self.request.GET.get('search')
        queryset = queryset.filter(is_published=True)
        if category and category != 'None':
            queryset = queryset.filter(category__slug=category)
        if search and search.strip():
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

class ActualitesListView(ListView):
    model = Actualites
    template_name = 'actualites.html'
    context_object_name = 'actualites'

    def get_queryset(self):
        return Actualites.objects.filter(is_published=True).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actualites = self.get_queryset()
        # Supprimez cette ligne qui cause l'erreur
        # categories = SoftwareCategory.objects.filter(news__in=news_list).distinct()
        # context['categories'] = categories
        return context

class ActualitesDetailView(DetailView):
    model = Actualites
    template_name = 'actualite_detail.html'
    context_object_name = 'actualite'  # Ajoutez cette ligne

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter à 49 caractères
        
        return get_object_or_404(queryset, slug=clean_slug, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def alternative_detail(request, slug):
    software = get_object_or_404(Software, slug=slug)
    alternatives = Software.objects.filter(category__in=software.category.all()).exclude(id=software.id).distinct()
    
    context = {
        'software': software,
        'alternatives': alternatives,
    }
    return render(request, 'alternative_detail.html', context)

from django.utils.safestring import mark_safe

class SoftwareDetailView(DetailView):
    model = Software
    template_name = 'software_detail.html'
    context_object_name = 'software'
    
    def get_queryset(self):
        return Software.objects.prefetch_related('category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Créer une clé unique pour ce logiciel dans la session
        viewed_softwares = self.request.session.get('viewed_softwares', [])
        
        # Si l'ID du logiciel n'est pas dans la session, on incrémente le compteur
        if obj.id not in viewed_softwares:
            # Incrémenter le compteur de manière atomique
            Software.objects.filter(id=obj.id).update(unique_views=F('unique_views') + 1)
            
            # Rafraîchir l'objet depuis la base de données
            obj.refresh_from_db()
            
            # Ajouter l'ID à la liste des logiciels vus
            viewed_softwares.append(obj.id)
            self.request.session['viewed_softwares'] = viewed_softwares
            
            # Définir une expiration de session après 24h
            self.request.session.set_expiry(86400)  # 24 heures en secondes
        
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        software = self.object
        categories = software.category.all()

        # Optimisation de la requête pour les logiciels similaires
        similar_softwares = (
            Software.objects.filter(
                is_published=True,
                category__in=categories
            )
            .exclude(id=software.id)
            .prefetch_related('category')
            .distinct()
            .annotate(
                common_categories=Count(
                    'category',
                    filter=Q(category__in=categories)
                )
            )
            .order_by('-common_categories')[:3]
        )

        from datetime import date
        start_date = date(2024, 11, 10)
        days_since = (date.today() - start_date).days

        context.update({
            'similar_softwares': similar_softwares,
            'days_since': days_since,
        })
        return context
    
from django.views.generic import TemplateView

class Custom404View(TemplateView):
    template_name = '404.html'

# Ajoutez cette fonction à la fin du fichier
def custom_404_view(request, exception):
    return Custom404View.as_view()(request, exception=exception)

def robots_txt(request):
    return render(request, 'robots.txt', content_type='text/plain')


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_redirect_view(request, old_path, slug, r_id=None):
    # Décoder l'URL pour gérer les caractères spéciaux
    decoded_slug = unquote(slug)
    
    # Chercher la redirection dans notre dictionnaire
    redirect_key = (old_path, decoded_slug, r_id) if r_id else (old_path, decoded_slug)
    new_path = REDIRECTIONS.get(redirect_key)
    
    if new_path:
        return redirect(new_path, permanent=True)
        
    # Si aucune redirection n'est trouvée, continuer avec la logique existante
    # ... (garder le code existant pour les autres cas)