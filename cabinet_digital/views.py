from django.shortcuts import render
from .models import Software, SoftwareCategory, Article, News
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView


class ArticleListView(ListView):
    model = Article
    template_name = "article_list.html"

class ArticleDetailView(DetailView):
    model = Article
    template_name = "article_detail.html"

def home(request):
    return render(request, 'home.html')  # Create a home.html template

def contact(request):
    return render(request, 'contact.html')

def software_detail(request, slug):
    software = get_object_or_404(Software, slug=slug)
    categories = software.category.all()
    # Get all softwares except the current one
    all_softwares = Software.objects.exclude(slug=slug)
    
    similar_softwares = [
        {
            'software': s,
            'common_categories': len(set(s.category.all()) & set(categories))
        }
        for s in all_softwares
    ]
    
    # Sort by number of common categories and then take the top 3
    similar_softwares.sort(key=lambda x: x['common_categories'], reverse=True)
    similar_softwares = similar_softwares[:3]
    print(similar_softwares)
    context = {
        'similar_softwares': similar_softwares,
        'software': software,
    }
    return render(request, 'software_detail.html', context)

class CategoryListView(ListView):
    model = SoftwareCategory
    template_name = 'category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = SoftwareCategory
    template_name = 'category_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context['category'] = category
        context['softwares'] = Software.objects.filter(category=category)
        context['articles'] = Article.objects.filter(category=category)
        return context


def similar_software(request, software_slug):
    software = get_object_or_404(Software, slug=software_slug)
    categories = software.category.all()
    similar_softwares = Software.objects.filter(category__in=categories).exclude(id=software.id).distinct()[:3]
    
    context = {
        'similar_softwares': similar_softwares,
        'software': software,
    }
    return render(request, 'similar_software.html', context)


class SoftwareListView(ListView):
    model = Software
    template_name = 'software_list.html'
    context_object_name = 'softwares'
    paginate_by = 9  # Default value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SoftwareCategory.objects.all()
        context['selected_category'] = self.request.GET.get('categorie')
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-is_top_pick', 'name')
        category = self.request.GET.get('categorie')
        search = self.request.GET.get('search')
        if category:
            queryset = queryset.filter(category__slug=category)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return super().get(request, *args, **kwargs)

class NewsListView(ListView):
    model = News
    template_name = 'news.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return News.objects.filter(is_published=True).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news_list = self.get_queryset()
        categories = SoftwareCategory.objects.filter(news__in=news_list).distinct()
        context['categories'] = categories
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
