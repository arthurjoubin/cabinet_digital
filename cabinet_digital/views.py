from django.shortcuts import render
from .models import Software, SoftwareCategory, Article
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
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
    category = software.category
    return render(request, 'software_detail.html', {'software': software, 'category': software.category})


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


def similar_software(request, software_id):
    software = get_object_or_404(Software, id=software_id)
    categories = software.category.all()
    similar_softwares = Software.objects.filter(category__in=categories).exclude(id=software.id).distinct()[:3]
    print(similar_softwares)
    context = {
        'similar_softwares': similar_softwares,
        'software': software,
    }
    return render(request, 'similar_software.html', context)


class SoftwareListView(ListView):
    model = Software
    template_name = 'software_list.html'
    context_object_name = 'softwares'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SoftwareCategory.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-is_top_pick', 'name')
        slug = self.request.GET.get('categorie')
        search = self.request.GET.get('search')
        if slug:
            queryset = queryset.filter(category__slug=slug)
        if search:
            queryset = queryset.filter(Q(name__icontains=search))
        print(f"Nombre de logiciels trouvés : {queryset.count()}")
        return queryset
    

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.htmx:
            return render(request, 'software_list_partial.html', context)
        return super().get(request, *args, **kwargs)
