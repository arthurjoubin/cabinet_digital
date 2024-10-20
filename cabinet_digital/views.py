from django.shortcuts import render
from .models import Software, SoftwareCategory, Article, Actualites
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.views.generic import ListView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
import openai
from django.conf import settings
from openai import OpenAI
from django.utils.safestring import mark_safe
import markdown
from markdown import markdown
from django.db.models import Count  
from django.http import Http404
from django.shortcuts import redirect
from django.utils.text import slugify
import unidecode
from urllib.parse import unquote
import os
from django.utils.html import escape

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
        ).order_by('name')

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
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SoftwareCategory.objects.annotate(
            software_count=Count('categories_softwares_link')
        ).order_by('name')
        context['selected_category'] = self.request.GET.get('categorie')
        context['search_query'] = self.request.GET.get('search', '')
        return context
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-is_top_pick', 'name')
        queryset = queryset.filter(is_published=True, slug__isnull=False).exclude(slug='')
        category = self.request.GET.get('categorie')
        search = self.request.GET.get('search')
        queryset = queryset.filter(is_published=True)
        if category and category != 'None':  # Check if category is not None or 'None'
            queryset = queryset.filter(category__slug=category)
        if search and search.strip():  # Check if search is not empty or just whitespace
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

class ActualitesListView(ListView):
    model = Actualites
    template_name = 'actualites.html'
    context_object_name = 'actualites'

    def get_queryset(self):
        return Actualites.objects.filter(is_published=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actualites = self.get_queryset()
        # Supprimez cette ligne qui cause l'erreur
        # categories = SoftwareCategory.objects.filter(news__in=news_list).distinct()
        # context['categories'] = categories
        return context

class ActualitesDetailView(DetailView):
    model = Actualites
    template_name = 'actualites_detail.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter à 49 caractères
        
        return get_object_or_404(queryset, slug=clean_slug, is_published=True)

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
                software.video = mark_safe(f'<img src="{escape(software.video)}" alt="Image de la solution" height="220">')
            elif 'youtube.com' in software.video or 'youtu.be' in software.video:
                video_id = software.video.split('v=')[-1] if 'v=' in software.video else software.video.split('/')[-1]
                software.video = mark_safe(f'''
                <iframe width="560" height="315" src="https://www.youtube.com/embed/{escape(video_id)}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
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

@staff_member_required
def ai_text_processor(request):
    context = {
        'prompt': "Mets en forme le texte en markdown. Utilise du gras et des bullets points. N'ajoute pas ''' markdown ''' ou autres instructions.",
        'HTMX_SCRIPT': settings.HTMX_SCRIPT,
    }
    
    if request.method == 'POST':
        text = request.POST.get('text')
        prompt = request.POST.get('prompt', context['prompt'])
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        
        ai_response = response.choices[0].message.content
        output = markdown(ai_response)
        return render(request, 'ai_text_processor_output.html', {'output': output})
    
    return render(request, 'ai_text_processor.html', context)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_redirect_view(request, old_path, slug, any_value):
    # Mapping des anciens chemins vers les nouveaux
    path_mapping = {
        'solution': 'logiciels',
        'news': 'actualites',
        'article': 'articles',
        'categorie': 'categories'
    }

    # Décoder l'URL pour gérer les caractères spéciaux
    decoded_slug = unquote(slug)
    # Supprimer les accents et appliquer slugify
    unaccented_slug = unidecode.unidecode(decoded_slug)
    new_slug = slugify(unaccented_slug)

    # Obtenir le nouveau chemin
    new_path = path_mapping.get(old_path, old_path)

    # Construire l'URL de redirection
    redirect_url = f'/{new_path}/{new_slug}/'
    return redirect(redirect_url, permanent=True)
