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
from django.urls import path, include
from cabinet_digital import views
from cabinet_digital.views import ArticleListView, ArticleDetailView, CategoryListView, CategoryDetailView, NewsListView, NewsDetailView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [

    path('admin/', admin.site.urls),
    path('logiciels/',  views.SoftwareListView.as_view(), name='software_list'),
    path('', views.home, name='home'),
    path('logiciels/<str:slug>/', views.software_detail, name='software_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('articles/', ArticleListView.as_view(), name='articles'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('contact/', views.contact, name='contact'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('actualites/', NewsListView.as_view(), name='news_list'),  # Changé de 'news' à 'news_list'
    path('actualites/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
