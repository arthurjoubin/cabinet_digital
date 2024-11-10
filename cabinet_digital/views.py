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

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        if not slug:
            raise Http404("Aucun slug fourni pour le logiciel.")
        
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter à 49 caractères
        
        try:
            software = queryset.get(slug=clean_slug, is_published=True)
        except Software.DoesNotExist:
            raise Http404(f"Le logiciel publié avec le slug '{clean_slug}' n'existe pas.")
        
        return software

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        software = self.object

        if software.video:
            if software.video.endswith('.webp'):
                software.video = mark_safe(f'<img src="{escape(software.video)}" alt="Image de la solution" height="220" loading="lazy">')
            elif 'youtube.com' in software.video or 'youtu.be' in software.video:
                video_id = software.video.split('v=')[-1] if 'v=' in software.video else software.video.split('/')[-1]
                software.video = mark_safe(f'''
                <iframe width="560" height="315" src="https://www.youtube.com/embed/{escape(video_id)}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
                ''')

        categories = software.category.all()
        all_softwares = Software.objects.filter(is_published=True).exclude(slug=software.slug)
        
        similar_softwares = [
            s for s in all_softwares
            if set(s.category.all()) & set(categories)
        ]
        
        similar_softwares.sort(key=lambda x: len(set(x.category.all()) & set(categories)), reverse=True)
        similar_softwares = similar_softwares[:3]
        
        from datetime import datetime, date
        start_date = date(2024, 9, 26)
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

def custom_redirect_view(request, old_path, slug):
    path_mapping = {
        'solution': 'logiciels',
        'news': 'actualites',
        'article': 'articles',
        'categorie': 'categories'
    }
    new_path = path_mapping.get(old_path, old_path)
    print(slug)
    # Construire l'URL de redirection
    redirect_url = f'/{new_path}/{slug}/'
    return redirect(redirect_url, permanent=True)