from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.views.generic import ListView, DetailView, TemplateView
from .models import (
    Software, SoftwareCategory, Actualites, Tag, Metier, AIModel, 
    AIArticle, ProviderAI, Integrator, PlatformeDematerialisation, Company, Contact, ContactIntegrator
)
from django.conf import settings
from django.db.models import Count, Prefetch, Q, F, Sum, Avg
from django.utils.text import slugify
from django.db.models.functions import Lower
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.contrib import messages
import logging
from django.template.loader import get_template
from datetime import date
import unidecode
from urllib.parse import unquote
from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import json
import re
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator



logger = logging.getLogger(__name__)




def home(request):
    context = {
        'avis_screenshot': '/static/marketing/avis_screenshot.png',
    }
    return render(request, 'home.html', context)



def contact(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        entreprise = request.POST.get('entreprise')
        message = request.POST.get('message')
        
        # Validation basique
        if not all([nom, email, entreprise, message]):
            messages.error(request, 'Tous les champs sont obligatoires.')
            return render(request, 'contact.html')
        
        # Sauvegarde en base
        contact_obj = Contact.objects.create(
            nom=nom,
            email=email,
            entreprise=entreprise,
            message=message
        )
        
        # Envoi de l'email avec logs détaillés
        try:
            logger.info(f"Tentative d'envoi d'email de contact pour {nom} ({email})")
            
            subject = f"Cabinet Digital x {entreprise} - Prise de contact"
            email_message = f"""
DE : {nom} ({email})

MESSAGE :
{message}


DATE : {contact_obj.date_creation.strftime('%d/%m/%Y à %H:%M')}

            """
            
            logger.info(f"Envoi email de contact de '{email}' vers '{settings.DEFAULT_FROM_EMAIL}'")
            
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            logger.info("Email de contact envoyé avec succès !")
            
            # Retourner la popup pour HTMX
            return render(request, 'contact_success_popup.html', {'contact': contact_obj})
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'email de contact: {str(e)}")
            logger.error(f"Type d'erreur: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            
            # Même en cas d'erreur d'email, on affiche la popup de succès
            return render(request, 'contact_success_popup.html', {'contact': contact_obj})
    
    return render(request, 'contact.html')



class CategoryListView(ListView):
    model = SoftwareCategory
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    def get_queryset(self):
        queryset = SoftwareCategory.objects.filter(is_published=True).annotate(
            software_count=Count('categories_softwares_link', filter=Q(categories_softwares_link__is_published=True))
        ).filter(software_count__gt=0)

        # Filtre par métier si spécifié
        metier_slug = self.request.GET.get('metier')
        if metier_slug:
            queryset = queryset.filter(metier__slug=metier_slug)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter la liste des métiers pour le filtre
        context['metiers'] = Metier.objects.all().order_by('name')
        context['selected_metier'] = self.request.GET.get('metier')
        
        # Ajouter les éléments du breadcrumb
        breadcrumb = [
            {'title': 'Catégories', 'url': None}
        ]
        
        # Si un métier est sélectionné, l'ajouter au breadcrumb
        selected_metier = self.request.GET.get('metier')
        if selected_metier:
            try:
                metier = Metier.objects.get(slug=selected_metier)
                breadcrumb = [
                    {'title': metier.name, 'url': reverse('metier_detail', kwargs={'slug': metier.slug})},
                    {'title': 'Catégories', 'url': None}
                ]
            except Metier.DoesNotExist:
                pass
                
        context['breadcrumb_items'] = breadcrumb
        return context

class CategoryDetailView(DetailView):
    model = SoftwareCategory
    template_name = 'categories/category_detail.html'
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter  49 caractères
        
        # Chercher la catégorie avec le slug nettoyé
        return get_object_or_404(queryset, slug=clean_slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context['category'] = category
        context['count'] = Software.objects.filter(category=category, is_published=True).count()
        context['softwares'] = Software.objects.filter(category=category, is_published=True)
        context['canonical_url'] = self.request.build_absolute_uri(self.object.get_absolute_url())
        # Ajouter le métier au contexte
        context['metier'] = category.metier
        
        # Ajouter les éléments du breadcrumb
        breadcrumb = []
        
        # Si la catégorie a un métier associé, l'ajouter au breadcrumb
        if category.metier:
            breadcrumb.append({
                'title': category.metier.name, 
                'url': reverse('metier_detail', kwargs={'slug': category.metier.slug})
            })
        
        # Ajouter la catégorie actuelle au breadcrumb
        breadcrumb.append({'title': category.name, 'url': None})
        
        context['breadcrumb_items'] = breadcrumb
        
        return context

class SoftwareListView(ListView):
    model = Software
    template_name = 'software/software_list.html'
    context_object_name = 'softwares'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        
        # Get all published categories for the filter
        context['categories'] = SoftwareCategory.objects.filter(is_published=True).order_by('name')
        
        # Ajouter les éléments du breadcrumb - Par défaut Accueil > Logiciels
        breadcrumb = [
            {'title': 'Logiciels', 'url': None}
        ]
        
        context['breadcrumb_items'] = breadcrumb
                
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-is_top_pick', Lower('name'))
        queryset = queryset.filter(is_published=True, slug__isnull=False).exclude(slug='')
        
        # Handle search filter
        search = self.request.GET.get('search')
        if search and search.strip():
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Handle category filter
        category = self.request.GET.get('category')
        if category and category.strip():
            queryset = queryset.filter(category__slug=category)
            
        return queryset

class ActualitesListView(ListView):
    model = Actualites
    template_name = 'news/actualites.html'
    context_object_name = 'actualites'
    paginate_by = 12
    
    def get_queryset(self):
        # Start with published actualités
        queryset = Actualites.objects.filter(is_published=True)
        
        # Filter by tag if provided
        selected_tag = self.request.GET.get('tag', '').strip()
        if selected_tag:
            queryset = queryset.filter(tags__slug=selected_tag)
        
        # Order by publication date
        return queryset.order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add current year
        current_year = timezone.now().year
        context['current_year'] = current_year
        
        # Count actualités from current year only
        context['total_actualites'] = Actualites.objects.filter(
            is_published=True,
            pub_date__year=current_year
        ).count()
        
        # Add only tags that have at least one published actualité
        context['tags'] = Tag.objects.filter(
            actualites__is_published=True
        ).distinct().order_by('name')
        context['selected_tag'] = self.request.GET.get('tag', '')
        
        # Add breadcrumb items
        context['breadcrumb_items'] = [
            {'title': 'Actualités', 'url': None}
        ]
        
        return context

class ActualitesDetailView(DetailView):
    model = Actualites
    template_name = 'news/actualite_detail.html'
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
        # Ajouter les éléments du breadcrumb
        context['breadcrumb_items'] = [
            {'title': 'Actualités', 'url': reverse('actualites')}        ]
        return context

def alternative_detail(request, slug):
    """Page dédiée aux alternatives avec SEO optimisé"""
    software = get_object_or_404(Software, slug=slug)
    categories = software.category.all()
    
    # Récupérer les alternatives avec un compteur de catégories communes
    if categories.exists():
        alternatives = Software.objects.filter(
            category__in=categories,
            is_published=True
        ).exclude(
            id=software.id
        ).annotate(
            common_categories=Count(
                'category', 
                filter=Q(category__in=categories),
                distinct=True
            )
        ).order_by(
            '-common_categories',  # D'abord par nombre de catégories communes
            '-is_top_pick',        # Ensuite par top pick
            'name'                # Enfin par ordre alphabétique
        ).distinct()
    else:
        # Si le logiciel n'a pas de catégories, prendre des logiciels aléatoires
        alternatives = Software.objects.filter(
            is_published=True
        ).exclude(
            id=software.id
        ).order_by('-is_top_pick', 'name')
    
    context = {
        'software': software,
        'alternatives': alternatives,
    }
    return render(request, 'alternatives/alternative_detail.html', context)

def software_integrators(request, slug):
    software = get_object_or_404(Software, slug=slug)
    
    # Récupérer les intégrateurs qui implémentent ce logiciel
    integrators = Integrator.objects.filter(
        softwares=software,
        is_published=True
    ).order_by('-is_top_pick', 'name')
    
    context = {
        'software': software,
        'integrators': integrators,
    }
    return render(request, 'software/software_integrators.html', context)

from django.utils.safestring import mark_safe

class SoftwareDetailView(DetailView):
    model = Software
    template_name = 'software/software_detail.html'
    context_object_name = 'software'
    
    def dispatch(self, request, *args, **kwargs):
        # Cache for all users
        return cache_page(60 * 15)(super().dispatch)(request, *args, **kwargs)
    
    def get_queryset(self):
        # Préchargement des catégories pour l'affichage
        return super().get_queryset().prefetch_related(
            'category', 
            'category__metier', 
        )
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        # Décoder et nettoyer le slug
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]  # Limiter  49 caractères
        
        # Chercher la catégorie avec le slug nettoyé
        obj = get_object_or_404(queryset, slug=clean_slug)
        
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        software = self.object
        
        # Ajouter les alternatives (logiciels de la même catégorie)
        # Récupérer toutes les catégories du logiciel actuel
        software_categories = software.category.all()
        
        if software_categories.exists():
            # Trouver les logiciels qui partagent au moins une catégorie
            alternatives = Software.objects.filter(
                category__in=software_categories,
                is_published=True
            ).exclude(
                id=software.id
            ).annotate(
                # Compter le nombre de catégories communes
                common_categories=Count(
                    'category', 
                    filter=Q(category__in=software_categories),
                    distinct=True
                )
            ).select_related('company').prefetch_related('category').order_by(
                '-common_categories',  # D'abord par nombre de catégories communes
                '-is_top_pick',        # Ensuite par top pick
                'name'                 # Enfin par ordre alphabétique
            ).distinct()[:12]
        else:
            # Si le logiciel n'a pas de catégories, prendre des logiciels aléatoires
            alternatives = Software.objects.filter(
                is_published=True
            ).exclude(
                id=software.id
            ).select_related('company').prefetch_related('category').order_by(
                '-is_top_pick',
                'name'
            )[:12]
        
        context['alternatives'] = alternatives
        
        # Récupérer les intégrateurs qui implémentent ce logiciel
        context['integrators'] = Integrator.objects.filter(
            softwares=software,
            is_published=True
        ).order_by('-is_top_pick', 'name')[:9]  # Limite à 9 intégrateurs
        

                
        # Ajouter l'URL canonique
        context['canonical_url'] = self.request.build_absolute_uri(self.object.get_absolute_url())
        
        # Calculate days since creation (assuming last_modified was set at creation)
        if software.last_modified:
            days_since = (timezone.now().date() - software.last_modified.date()).days
            context['days_since'] = days_since
        else:
            context['days_since'] = 0
            
        # Ajouter les éléments du breadcrumb
        breadcrumb = []
        
        # Si le logiciel a des catégories, ajouter la première au breadcrumb
        if software.category.all().exists():
            category = software.category.first()
            
            # Si la catégorie a un métier, l'ajouter au breadcrumb
            if category.metier:
                breadcrumb.append({
                    'title': category.metier.name, 
                    'url': reverse('metier_detail', kwargs={'slug': category.metier.slug})
                })
            
            # Ajouter la catégorie au breadcrumb
            breadcrumb.append({
                'title': category.name, 
                'url': reverse('category_detail', kwargs={'slug': category.slug})
            })
        
        # Ajouter le logiciel au breadcrumb
        breadcrumb.append({'title': software.name, 'url': None})
            
        context['breadcrumb_items'] = breadcrumb
        
        # Ajouter les articles liés à l'éditeur (Company)
        if software.company:
            context['related_articles'] = Actualites.objects.filter(
                company=software.company,
                is_published=True
            ).order_by('-pub_date')[:3]  # Limiter à 3 articles récents
        
        # Check if we should show integrators tab by default
        if self.request.GET.get('tab') == 'integrators' or self.request.resolver_match.url_name == 'software_integrators_seo':
            context['active_tab'] = 'integrators'
            
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
    
    # Supprimer les accents avant d'appliquer slugify
    unaccented_slug = unidecode.unidecode(decoded_slug)
    
    # Si c'est une catégorie et que le slug commence par "logiciel_"
    if old_path == "categorie" and unaccented_slug.startswith("logiciel_"):
        # Retirer le préfixe "logiciel_"
        unaccented_slug = unaccented_slug[9:]  # 9 est la longueur de "logiciel_"
    
    # Appliquer slugify sur le slug sans accent
    new_slug = slugify(unaccented_slug)
    
    # Définir le target_path en fonction du old_path
    path_mapping = {
        'solution': 'logiciels',
        'news': 'actualites', 
        'article': 'actualites',
        'categorie': 'categories'
    }
    target_path = path_mapping.get(old_path, old_path)
    
    # Construire l'URL de redirection
    redirect_url = f'/{target_path}/{new_slug}/'
    return redirect(redirect_url, permanent=True)
        

def roi_calculateur(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            months_projection = int(request.POST.get('months_projection', 24))
            
            data = {
                'monthly_cost_saas': float(request.POST.get('monthly_cost_saas', 0)),
                'one_time_cost_saas': float(request.POST.get('one_time_cost_saas', 0)),
                'integrator_cost_implementation': float(request.POST.get('integrator_cost_implementation', 0)),
                'integrator_maintenance': float(request.POST.get('integrator_maintenance', 0)),
                'internal_hours_internal_implementation': float(request.POST.get('internal_hours_internal_implementation', 0)),
                'cost_per_hour_internal_implementation': float(request.POST.get('cost_per_hour_internal_implementation', 0)),
                'employee_hours_per_week_gained': float(request.POST.get('employee_hours_per_week_gained', 0)),
                'cost_of_employee_hour': float(request.POST.get('cost_of_employee_hour', 0)),
                'other_savings': float(request.POST.get('other_savings', 0))
            }
            
            # Initialisation des listes
            months = list(range(months_projection + 1))  # +1 pour inclure le mois 0
            cumulative_costs = []
            cumulative_savings = []
            net_roi = []

            # Calcul des coûts fixes initiaux
            fixed_costs = (
                data['one_time_cost_saas'] +
                data['integrator_cost_implementation'] +
                (data['internal_hours_internal_implementation'] * data['cost_per_hour_internal_implementation'])
            )

            # Calcul des heures économisées par mois
            monthly_hours_saved = data['employee_hours_per_week_gained'] * 4

            # Calcul mois par mois sur la période demandée
            for month in range(months_projection + 1):  # Utiliser months_projection au lieu de 24
                # Coûts cumulés avec maintenance
                monthly_costs = fixed_costs + (data['monthly_cost_saas'] * month) + (data['integrator_maintenance'] * month)
                
                # Gains cumulés
                monthly_savings = (
                    (monthly_hours_saved * data['cost_of_employee_hour'] * month) +
                    (data['other_savings'] * month)
                )
                
                # ROI net
                net = monthly_savings - monthly_costs

                cumulative_costs.append(round(monthly_costs, 2))
                cumulative_savings.append(round(monthly_savings, 2))
                net_roi.append(round(net, 2))

            # Point d'équilibre
            break_even = next((i for i, x in enumerate(net_roi) if x > 0), -1)

            # Économies mensuelles moyennes
            monthly_savings = (monthly_hours_saved * data['cost_of_employee_hour']) + data['other_savings']

            # S'assurer que toutes les listes ont la bonne longueur
            assert len(cumulative_costs) == months_projection + 1
            assert len(cumulative_savings) == months_projection + 1
            assert len(net_roi) == months_projection + 1

            chart_data = {
                'labels': months,
                'costs': cumulative_costs,
                'savings': cumulative_savings,
                'net': net_roi,
                'break_even': break_even,
                'monthly_savings': round(monthly_savings, 2)
            }
            
            return JsonResponse(chart_data)
            
        except Exception as e:
            logger.error(f"Erreur dans le calcul ROI : {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    try:
        template = get_template('outils/roi_calculateur.html')
        logger.info(f"Template trouvé : {template.origin.name}")
        logger.info(f"Template dirs : {settings.TEMPLATES[0]['DIRS']}")
        logger.info("Tentative de rendu du template roi_calculateur.html")
        response = render(request, 'outils/roi_calculateur.html')
        logger.info(f"Contenu de la réponse : {response.content}")
        logger.info("Rendu du template réussi")
        return response
    except Exception as e:
        logger.error(f"Erreur lors du rendu : {str(e)}")
        raise

def immobilier_calculateur(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            years_projection = int(request.POST.get('years_projection', 25))
            
            data = {
                'property_cost': float(request.POST.get('property_cost', 0)),
                'notary_fees': float(request.POST.get('notary_fees', 0)),
                'total_loan': float(request.POST.get('total_loan', 0)),
                'monthly_payment': float(request.POST.get('monthly_payment', 0)),
                'interest_rate': float(request.POST.get('interest_rate', 0)),
                'down_payment': float(request.POST.get('down_payment', 0)),
                'rent_saved': float(request.POST.get('rent_saved', 0)),
                'property_tax': float(request.POST.get('property_tax', 0)),
                'insurance': float(request.POST.get('insurance', 0)),
                'maintenance': float(request.POST.get('maintenance', 0)),
                'condo_fees': float(request.POST.get('condo_fees', 0))
            }
            
            yearly_costs = []
            yearly_savings = []
            yearly_net = []
            property_value = []  # Pour suivre l'évolution de la valeur du bien
            loan_remaining = []  # Pour suivre le capital restant à rembourser
            
            # Coûts initiaux
            initial_costs = data['property_cost'] + data['notary_fees'] - data['down_payment']
            
            # Calculs annuels
            for year in range(years_projection + 1):
                # Coûts annuels
                yearly_mortgage = data['monthly_payment'] * 12
                yearly_expenses = (
                    data['property_tax'] +
                    data['insurance'] * 12 +
                    data['maintenance'] * 12 +
                    data['condo_fees'] * 12
                )
                
                total_costs = initial_costs if year == 0 else yearly_mortgage + yearly_expenses
                
                # Gains annuels
                yearly_rent_saved = data['rent_saved'] * 12
                property_appreciation = data['property_cost'] * (1 + 0.02) ** year  # 2% d'appréciation annuelle
                
                # Calcul du capital restant (simplifié)
                remaining_loan = max(0, data['total_loan'] * (1 - year/years_projection)) if year <= years_projection else 0
                
                # Cumuls
                yearly_costs.append(round(total_costs, 2))
                yearly_savings.append(round(yearly_rent_saved, 2))
                yearly_net.append(round(yearly_rent_saved - total_costs, 2))
                property_value.append(round(property_appreciation, 2))
                loan_remaining.append(round(remaining_loan, 2))

            # Point d'équilibre (en années)
            break_even = next((i for i, x in enumerate(yearly_net) if x > 0), -1)

            chart_data = {
                'years': list(range(years_projection + 1)),
                'costs': yearly_costs,
                'savings': yearly_savings,
                'net': yearly_net,
                'property_value': property_value,
                'loan_remaining': loan_remaining,
                'break_even': break_even,
                'yearly_savings': round(data['rent_saved'] * 12, 2)
            }
            
            return JsonResponse(chart_data)
            
        except Exception as e:
            logger.error(f"Erreur dans le calcul immobilier : {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'outils/immobilier_calculateur.html')

def generate_python_script(data):
    # Normaliser les chemins en remplaçant les backslashes par des forward slashes
    local_path = data["local_path"].replace('\\', '/')
    remote_path = data["remote_path"].replace('\\', '/')
    archive_path = data["archive_path"].replace('\\', '/') if data.get("archive_path") else ""
    key_path = data["key_path"].replace('\\', '/') if data.get("key_path") else ""

    script = """import paramiko
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_file = 'sftp_transfer.log'
    
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    handler.setFormatter(log_formatter)
    
    logger = logging.getLogger('sftp_transfer')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

logger = setup_logging()

def safe_transfer(func, src, dst, description):
    try:
        func(src, dst)
        logger.info(f"{description} réussi: {os.path.basename(src)}")
        return True
    except Exception as e:
        logger.error(f"{description} échoué: {os.path.basename(src)} - {str(e)}")
        return False

def sftp_transfer():
    ssh = None
    sftp = None
    success_count = 0
    error_count = 0
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
"""

    # Authentification
    if data["auth_type"] == "password":
        script += f"""
        ssh.connect("{data['host']}", {data['port']}, "{data['username']}", password="{data['password']}")"""
    else:
        if data["has_passphrase"]:
            script += f"""
        key = paramiko.RSAKey.from_private_key_file("{key_path}", password="{data['key_passphrase']}")"""
        else:
            script += f"""
        key = paramiko.RSAKey.from_private_key_file("{key_path}")"""
        script += f"""
        ssh.connect("{data['host']}", {data['port']}, "{data['username']}", pkey=key)"""

    script += """
        sftp = ssh.open_sftp()
        """

    # Action de transfert
    if data["action"] == "download":
        script += f"""
        os.makedirs("{local_path}", exist_ok=True)
        """
        
        if data["delete_after"] and archive_path:
            script += f"""
        os.makedirs("{archive_path}", exist_ok=True)
        """
            
        script += f"""
        try:
            remote_files = sftp.listdir("{remote_path}")
            total_files = len(remote_files)
            logger.info(f"{{total_files}} fichiers trouvés pour le transfert")

            for file in remote_files:
                remote_file_path = os.path.join("{remote_path}", file)
                local_file_path = os.path.join("{local_path}", file)
                
                try:
                    if safe_transfer(sftp.get, remote_file_path, local_file_path, "téléchargement"):
                        success_count += 1
                        
                        if {str(data["delete_after"]).lower()}:"""
        
        if data["delete_after"] and archive_path:
            script += f"""
                            remote_archive_path = os.path.join("{archive_path}", file)
                            if safe_transfer(sftp.rename, remote_file_path, remote_archive_path, "archivage"):
                                logger.info(f"Fichier archivé avec succès: {{file}}")"""
        else:
            script += """
                            try:
                                sftp.remove(remote_file_path)
                                logger.info(f"Fichier supprimé avec succès: {file}")
                            except Exception as e:
                                logger.error(f"Erreur lors de la suppression: {file} - {str(e)}")"""
                                
        script += """
                except Exception as e:
                    error_count += 1
                    logger.error(f"Erreur lors du traitement du fichier {file}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Erreur lors de la lecture du répertoire distant: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Erreur critique lors du transfert SFTP: {str(e)}")
        raise
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()
        
        logger.info(f"Transfert terminé: {success_count} succès, {error_count} erreurs")
        if error_count > 0:
            logger.warning("Certains fichiers n'ont pas pu être transférés. Consultez les logs pour plus de détails.")

if __name__ == '__main__':
    sftp_transfer()
"""
    return script

def sftp_generator(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Logs de débogage
            logger.info(f"Form data: {request.POST}")
            
            data = {
                'host': request.POST.get('host', ''),
                'port': int(request.POST.get('port', 22)),
                'username': request.POST.get('username', ''),
                'auth_type': request.POST.get('auth_type', 'password'),
                'password': request.POST.get('password', ''),
                'key_path': request.POST.get('key_path', ''),
                'local_path': request.POST.get('local_path', ''),
                'remote_path': request.POST.get('remote_path', ''),
                'action': request.POST.get('action', 'download'),
                'delete_after': request.POST.get('archiveAfter') == 'on',
                'archive_path': request.POST.get('archive_path', ''),
                'schedule_type': request.POST.get('schedule_type', 'none'),
                'schedule_time': request.POST.get('schedule_time', '00:00'),
                'has_passphrase': request.POST.get('has_passphrase') == 'on',
                'key_passphrase': request.POST.get('key_passphrase', ''),
            }
            
            # Logs de débogage
            logger.info(f"delete_after: {data['delete_after']}")
            logger.info(f"archive_path: {data['archive_path']}")
            logger.info(f"raw archiveAfter: {request.POST.get('archiveAfter')}")
            
            # Générer le script Python
            script_content = generate_python_script(data)
            
                        # Générer la commande de planification si nécessaire            schedule_command = ''            if data['schedule_type'] != 'none':                # TODO: Implémenter la génération de commandes de planification                schedule_command = f"# Planification {data['schedule_type']} à {data['schedule_time']}"
            
            response_data = {
                'script': script_content,
                'schedule_command': schedule_command
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Erreur dans la génération du script SFTP : {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'outils/sftp_generator.html')

def amortissement_calculateur(request, loan_type='immobilier'):
    # Define loan type configurations
    loan_configs = {
        'immobilier': {
            'title': 'Tableau d\'amortissement prêt immobilier 2025',
            'subtitle': 'Simulez votre crédit immobilier avec notre calculateur gratuit',
            'meta_title': 'Tableau d\'amortissement prêt immobilier 2025 | Simulateur gratuit avec Excel',
            'meta_description': 'Calculez gratuitement votre tableau d\'amortissement de prêt immobilier. Simulez vos mensualités, intérêts et capital restant dû. Export Excel/CSV inclus. ✓ Sans inscription',
            'keywords': 'tableau amortissement, prêt immobilier, simulation crédit immobilier 2025, calcul mensualités crédit, échéancier emprunt immobilier',
            'default_amount': 200000,
            'default_duration': 20,
            'default_rate': 4.1,
            'examples': [
                {'amount': 180000, 'duration': 25, 'rate': 4.0, 'rate_str': '4.0', 'label': 'Primo-accédant', 'description': 'Premier achat, appartement T3'},
                {'amount': 250000, 'duration': 20, 'rate': 4.2, 'rate_str': '4.2', 'label': 'Résidence principale', 'description': 'Maison familiale'},
                {'amount': 150000, 'duration': 15, 'rate': 3.8, 'rate_str': '3.8', 'label': 'Investissement locatif', 'description': 'Studio pour location'},
            ],
            'specificities': [
                'Durée maximale généralement de 25 à 30 ans',
                'Apport personnel recommandé de 10-20%',
                'Assurance emprunteur obligatoire',
                'Frais de notaire environ 7-8% du prix (ancien) ou 2-3% (neuf)'
            ]
        },
        'auto': {
            'title': 'Simulateur crédit auto',
            'subtitle': 'Calculez les mensualités de votre prêt automobile',
            'meta_title': 'Simulateur crédit auto 2025 | Calcul mensualités voiture',
            'meta_description': 'Simulez votre crédit auto et calculez vos mensualités. Tableau d\'amortissement complet avec export Excel. Comparez les offres de prêt automobile.',
            'keywords': 'crédit auto, prêt voiture, simulation crédit automobile, financement véhicule, calcul mensualités auto',
            'default_amount': 25000,
            'default_duration': 5,
            'default_rate': 5.5,
            'examples': [
                {'amount': 12000, 'duration': 4, 'rate': 4.9, 'rate_str': '4.9', 'label': 'Citadine occasion', 'description': 'Véhicule d\'occasion 3-5 ans'},
                {'amount': 28000, 'duration': 5, 'rate': 5.5, 'rate_str': '5.5', 'label': 'SUV neuf', 'description': 'Véhicule neuf familial'},
                {'amount': 45000, 'duration': 6, 'rate': 6.2, 'rate_str': '6.2', 'label': 'Véhicule premium', 'description': 'Berline ou SUV haut de gamme'},
            ],
            'specificities': [
                'Durée maximum généralement 7 ans pour un véhicule neuf',
                'Taux plus avantageux pour les véhicules neufs ou récents',
                'Apport personnel non obligatoire mais recommandé',
                'Assurance auto obligatoire pendant toute la durée',
                'Possibilité de LOA (Location avec Option d\'Achat) en alternative'
            ]
        },
        'personnel': {
            'title': 'Simulateur prêt personnel',
            'subtitle': 'Calculez votre crédit à la consommation',
            'meta_title': 'Simulateur prêt personnel 2025 | Crédit conso en ligne',
            'meta_description': 'Simulez votre prêt personnel et obtenez votre tableau d\'amortissement. Calcul des mensualités et du coût total de votre crédit consommation.',
            'keywords': 'prêt personnel, crédit consommation, simulation prêt perso, crédit conso, emprunt personnel',
            'default_amount': 15000,
            'default_duration': 3,
            'default_rate': 6.5,
            'examples': [
                {'amount': 8000, 'duration': 3, 'rate': 5.9, 'rate_str': '5.9', 'label': 'Travaux cuisine', 'description': 'Rénovation cuisine/salle de bain'},
                {'amount': 20000, 'duration': 4, 'rate': 6.8, 'rate_str': '6.8', 'label': 'Voiture + vacances', 'description': 'Financement multi-projets'},
                {'amount': 35000, 'duration': 6, 'rate': 7.5, 'rate_str': '7.5', 'label': 'Gros travaux', 'description': 'Rénovation complète maison'},
            ],
            'specificities': [
                'Montant minimum généralement 1 000€, maximum 75 000€',
                'Durée de remboursement de 6 mois à 7 ans maximum',
                'Aucune justification d\'utilisation des fonds requise',
                'Taux fixe pendant toute la durée du prêt',
                'Possibilité de remboursement anticipé sans pénalités'
            ]
        },
        'professionnel': {
            'title': 'Simulateur prêt professionnel',
            'subtitle': 'Financez votre activité professionnelle',
            'meta_title': 'Simulateur crédit professionnel 2025 | Prêt entreprise',
            'meta_description': 'Calculez votre prêt professionnel avec tableau d\'amortissement détaillé. Simulation crédit entreprise, artisan, commerçant. Export Excel gratuit.',
            'keywords': 'prêt professionnel, crédit entreprise, financement professionnel, prêt artisan, crédit TPE PME',
            'default_amount': 50000,
            'default_duration': 7,
            'default_rate': 4.5,
            'examples': [
                {'amount': 25000, 'duration': 5, 'rate': 3.8, 'rate_str': '3.8', 'label': 'Matériel professionnel', 'description': 'Équipements, véhicules utilitaires'},
                {'amount': 80000, 'duration': 10, 'rate': 4.5, 'rate_str': '4.5', 'label': 'Acquisition fonds', 'description': 'Rachat fonds de commerce'},
                {'amount': 150000, 'duration': 15, 'rate': 5.2, 'rate_str': '5.2', 'label': 'Immobilier pro', 'description': 'Achat local commercial/bureau'},
            ],
            'specificities': [
                'Garanties souvent exigées (hypothèque, nantissement)',
                'Étude de la viabilité du projet obligatoire',
                'Apport personnel généralement requis (20-30%)',
                'Durée variable selon le type d\'investissement',
                'Possibilité de différé de remboursement en début de prêt'
            ]
        }
    }
    
    # Get the loan configuration or default to immobilier
    config = loan_configs.get(loan_type, loan_configs['immobilier'])
    
    context = {
        'loan_type': loan_type,
        'config': config,
        'all_loan_types': [
            {'slug': 'immobilier', 'name': 'Prêt immobilier'},
            {'slug': 'auto', 'name': 'Crédit auto'},
            {'slug': 'personnel', 'name': 'Prêt personnel'},
            {'slug': 'professionnel', 'name': 'Prêt professionnel'},
        ]
    }
    
    return render(request, 'outils/amortissement_calculateur.html', context)

def outils(request):
    return render(request, 'outils/outils.html')

def actualites(request):
    # Récupérer tous les tags
    tags = Tag.objects.all()
    
    # Récupérer le tag sélectionné depuis l'URL et le nettoyer
    selected_tag = request.GET.get('tag', '').strip()
    
    # Debug logging
    logger.info(f"Tag sélectionné: '{selected_tag}'")
    
    # Commencer avec les actualités publiées
    actualites = Actualites.objects.filter(is_published=True)
    
    # Filtrer par tag si un tag est sélectionné
    if selected_tag:
        actualites = actualites.filter(tags__slug=selected_tag)
        logger.info(f"Nombre d'actualités après filtre: {actualites.count()}")
        logger.info(f"Query SQL: {actualites.query}")
    
    # Ordonner par date de publication
    actualites = actualites.order_by('-pub_date')
        
    context = {
        'actualites': actualites,
        'tags': tags,
        'selected_tag': selected_tag,
        'breadcrumb_items': [
            {'title': 'Actualités', 'url': None}
        ]
    }
    
    return render(request, 'news/actualites.html', context)

class AIModelListView(ListView):
    model = AIModel
    template_name = 'ai/model_list.html'
    context_object_name = 'models'
    paginate_by = 12

    def get_queryset(self):
        queryset = AIModel.objects.filter(is_published=True)
        
        # Filtres
        provider = self.request.GET.get('provider')
        if provider:
            queryset = queryset.filter(provider=provider)

        return queryset.distinct().order_by('-is_top_pick', Lower('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = AIModel.objects.values_list('provider', flat=True).distinct()
        return context

class AIModelDetailView(DetailView):
    model = AIModel
    template_name = 'ai/model_detail.html'
    context_object_name = 'model'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]
        
        obj = get_object_or_404(queryset, slug=clean_slug, is_published=True)
        

        
        return obj

class AIArticleListView(ListView):
    model = AIArticle
    template_name = 'ai/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        return context

    def get_queryset(self):
        return AIArticle.objects.filter(is_published=True).order_by('-pub_date')

class AIArticleDetailView(DetailView):
    model = AIArticle
    template_name = 'ai/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]
        
        return get_object_or_404(queryset, slug=clean_slug, is_published=True)

class ProviderDetailView(DetailView):
    model = ProviderAI
    template_name = 'ai/provider_detail.html'
    context_object_name = 'provider'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]
        
        return get_object_or_404(queryset, slug=clean_slug, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les modèles associés à cet éditeur
        context['provider_models'] = AIModel.objects.filter(
            provider=self.object,
            is_published=True
        ).order_by('-is_top_pick', 'name')
        return context

class MetierDetailView(DetailView):
    model = Metier
    template_name = 'metiers/metier_detail.html'
    context_object_name = 'metier'
    paginate_by = 12

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]
        
        return get_object_or_404(queryset, slug=clean_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        metier = self.object
        
        # Récupérer les catégories liées à ce métier
        context['metier_categories'] = SoftwareCategory.objects.filter(
            metier=metier,
            is_published=True
        ).annotate(
            software_count=Count('categories_softwares_link', 
                filter=Q(categories_softwares_link__is_published=True))
        ).filter(software_count__gt=0).order_by('name')
        
        # Récupérer les logiciels liés à ce métier (directement ou via catégories)
        softwares = Software.objects.filter(
            Q(metier=metier) | Q(category__metier=metier),
            is_published=True
        ).distinct()
        
        # Appliquer la recherche si présente
        search = self.request.GET.get('search')
        if search and search.strip():
            softwares = softwares.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        softwares = softwares.order_by('-is_top_pick', 'name')
        
        # Pagination des logiciels
        paginator = Paginator(softwares, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['softwares'] = page_obj
        context['page_obj'] = page_obj
        context['search_query'] = self.request.GET.get('search', '')
        
        # Ajouter les éléments du breadcrumb
        context['breadcrumb_items'] = [
            {'title': metier.name, 'url': None}
        ]
        
        return context



class IntegratorListView(ListView):
    model = Integrator
    template_name = 'integrators/integrator_list.html'
    context_object_name = 'integrators'
    paginate_by = 12
    
    def get_queryset(self):
        # Filter integrators that have a description and at least one linked software
        queryset = Integrator.objects.filter(
            is_published=True
        ).exclude(
            description=''
        ).exclude(
            description__isnull=True
        ).annotate(
            software_count=Count('softwares', filter=Q(softwares__is_published=True))
        ).filter(
            software_count__gt=0
        )
        
        # Handle search filter
        search = self.request.GET.get('search')
        if search and search.strip():
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # Handle software filter
        software_slug = self.request.GET.get('software')
        if software_slug:
            queryset = queryset.filter(softwares__slug=software_slug, softwares__is_published=True)
        
        return queryset.order_by('-is_top_pick', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_software'] = self.request.GET.get('software', '')
        
        # Get all published softwares that have at least one published integrator
        context['all_softwares'] = Software.objects.filter(
            is_published=True,
            integrators__is_published=True
        ).distinct().order_by('name')
        
        # Ajouter les éléments du breadcrumb
        breadcrumb = [
            {'title': 'Intégrateurs', 'url': None}
        ]
        
        context['breadcrumb_items'] = breadcrumb
        
        return context


class IntegratorDetailView(DetailView):
    model = Integrator
    template_name = 'integrators/integrator_detail.html'  
    context_object_name = 'integrator'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get(self.slug_url_kwarg)
        
        try:
            # Try to find by direct slug match
            obj = queryset.get(slug=slug)
        except Integrator.DoesNotExist:
            # If not found, try case-insensitive slug match
            try:
                obj = queryset.get(slug__iexact=slug)
            except Integrator.DoesNotExist:
                raise Http404(f"Aucun intégrateur correspondant à '{slug}' trouvé.")
        
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        integrator = self.object
        
        # Get partner softwares - only published ones
        context['partner_softwares'] = integrator.softwares.filter(is_published=True).order_by('name')
        
        # Add software solutions - direct implementation on frontend - only published ones
        context['software_solutions'] = integrator.softwares.filter(is_published=True).order_by('name')
        
        # Get similar integrators based on software implementations
        similar_integrators = []
        published_softwares = integrator.softwares.filter(is_published=True)
        if published_softwares.exists():
            # Find integrators that implement the same software solutions
            similar_by_software = Integrator.objects.filter(
                softwares__in=published_softwares,
                is_published=True
            ).exclude(id=integrator.id).distinct().annotate(
                common_count=Count('softwares', filter=Q(softwares__in=published_softwares))
            ).order_by('-common_count')[:5]  # Get more than 3 to have options
            
            similar_integrators.extend(list(similar_by_software))
        
        # If we don't have at least 3 similar integrators, add some random ones
        if len(similar_integrators) < 3:
            # Exclude already selected integrators
            random_integrators = Integrator.objects.filter(
                is_published=True
            ).exclude(id=integrator.id).exclude(
                id__in=[i.id for i in similar_integrators]
            ).order_by('?')[:3-len(similar_integrators)]
            
            similar_integrators.extend(list(random_integrators))
        
        # Limit to max 3 similar integrators
        context['similar_integrators'] = similar_integrators[:3]
        

        

        
        # Add breadcrumb items
        breadcrumb = [
            {'title': 'Intégrateurs', 'url': reverse('integrator_list')},
            {'title': integrator.name, 'url': None}
        ]
        context['breadcrumb_items'] = breadcrumb
        context['canonical_url'] = self.request.build_absolute_uri(integrator.get_absolute_url())
        
        return context


def contact_integrator(request):
    """Contact form for integrators (companies) wanting to be listed"""
    if request.method == 'POST':
        # Get form data
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        entreprise = request.POST.get('entreprise')
        site_web = request.POST.get('site_web')
        description = request.POST.get('description')
        logiciels_expertise = request.POST.get('logiciels_expertise')
        zone_intervention = request.POST.get('zone_intervention')
        
        # Validate required fields
        if not all([nom, email, entreprise, description, logiciels_expertise, zone_intervention]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'integrators/contact_integrator.html')
        
        # Create contact
        contact = ContactIntegrator.objects.create(
            nom=nom,
            email=email,
            entreprise=entreprise,
            site_web=site_web,
            description=description,
            logiciels_expertise=logiciels_expertise,
            zone_intervention=zone_intervention
        )
        
        # Send email notification
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"Cabinet Digital x {entreprise} - Demande d'ajout intégrateur"
            message = f"""
DE : {nom} ({email})

SITE WEB : {site_web}
ZONE D'INTERVENTION : {zone_intervention}
LOGICIELS D'EXPERTISE : {logiciels_expertise}

DESCRIPTION :
{description}


DATE : {contact.date_creation.strftime('%d/%m/%Y à %H:%M')}

            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
        
        messages.success(request, "Votre demande a été envoyée avec succès. Nous vous recontacterons prochainement.")
        return render(request, 'integrators/contact_integrator_success_popup.html')
    
    return render(request, 'integrators/contact_integrator.html')


class PDPListView(ListView):
    model = PlatformeDematerialisation
    template_name = 'pdp/pdp_list.html'
    context_object_name = 'pdps'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = PlatformeDematerialisation.objects.filter(is_published=True).order_by('name')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        # Filter by specialty - handle comma-separated tags
        specialty = self.request.GET.get('specialty')
        if specialty:
            # Create Q objects for each specialty tag to search within comma-separated values
            specialty_q = Q()
            # Split the search term and search for each part
            search_terms = [term.strip() for term in specialty.split(',')]
            for term in search_terms:
                if term:
                    specialty_q |= Q(specialty__icontains=term)
            
            # Also allow exact match for the full specialty filter value
            specialty_q |= Q(specialty__icontains=specialty)
            
            queryset = queryset.filter(specialty_q)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add breadcrumb
        breadcrumb = [
            {'title': 'Plateformes de Dématérialisation', 'url': None}
        ]
        context['breadcrumb_items'] = breadcrumb
        
        # Add search query to context
        context['search_query'] = self.request.GET.get('q', '')
        
        # Add specialty filter
        context['selected_specialty'] = self.request.GET.get('specialty', '')
        
        # Get all distinct specialties - extract individual tags from comma-separated values
        specialty_fields = PlatformeDematerialisation.objects.filter(
            is_published=True
        ).exclude(
            specialty=''
        ).values_list(
            'specialty', flat=True
        ).distinct()
        
        # Extract individual tags from comma-separated specialty fields
        all_specialties = set()
        for specialty_field in specialty_fields:
            if specialty_field:
                # Split by comma and clean up each tag
                tags = [tag.strip() for tag in specialty_field.split(',') if tag.strip()]
                all_specialties.update(tags)
        
        # Sort and create the specialties list
        context['specialties'] = [
            {'slug': s, 'name': s} 
            for s in sorted(all_specialties)
        ]
        
        return context


class PDPDetailView(DetailView):
    model = PlatformeDematerialisation
    template_name = 'pdp/pdp_detail.html'
    context_object_name = 'pdp'
    
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get(self.slug_url_kwarg)
        
        try:
            # Try to find by direct slug match
            obj = queryset.get(slug=slug, is_published=True)
        except PlatformeDematerialisation.DoesNotExist:
            # If not found, try case-insensitive slug match
            try:
                obj = queryset.get(slug__iexact=slug, is_published=True)
            except PlatformeDematerialisation.DoesNotExist:
                raise Http404(f"Aucune plateforme de dématérialisation correspondant à '{slug}' trouvée.")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pdp = self.object
        
        # Get related data
        pdp_integrators = pdp.integrators.filter(is_published=True)
        context['integrators'] = pdp_integrators
        context['connected_softwares'] = pdp.connected_softwares.filter(is_published=True)
        
        # Add software from the same company (editor) if available
        if pdp.company:
            # Software from the same company
            company_software = Software.objects.filter(
                company=pdp.company,
                is_published=True
            ).order_by('name')
            context['company_software'] = company_software
            
            # Intégrateurs partenaires des logiciels de l'éditeur
            if company_software.exists():
                software_integrators = Integrator.objects.filter(
                    softwares__in=company_software,
                    is_published=True
                ).exclude(
                    id__in=pdp_integrators.values_list('id', flat=True)
                ).distinct()
                
                if len(software_integrators) > 0:
                    context['software_integrators'] = software_integrators
        
        # Get similar PDPs - improved logic
        similar_pdps = []
        
        # First try to match by specialty if it exists
        if pdp.specialty:
            specialty_matches = PlatformeDematerialisation.objects.filter(
                specialty=pdp.specialty
            ).exclude(id=pdp.id).filter(is_published=True)[:3]
            similar_pdps.extend(list(specialty_matches))
            
        # If we need more, try connected softwares
        if len(similar_pdps) < 3 and pdp.connected_softwares.exists():
            software_matches = PlatformeDematerialisation.objects.filter(
                connected_softwares__in=pdp.connected_softwares.all()
            ).exclude(id=pdp.id).exclude(
                id__in=[p.id for p in similar_pdps]
            ).filter(is_published=True).distinct()[:3-len(similar_pdps)]
            similar_pdps.extend(list(software_matches))
            
        # If still need more, try integrators
        if len(similar_pdps) < 3 and pdp.integrators.exists():
            integrator_matches = PlatformeDematerialisation.objects.filter(
                integrators__in=pdp.integrators.all()
            ).exclude(id=pdp.id).exclude(
                id__in=[p.id for p in similar_pdps]
            ).filter(is_published=True).distinct()[:3-len(similar_pdps)]
            similar_pdps.extend(list(integrator_matches))
        
        # If we still have fewer than 3, add random PDPs
        if len(similar_pdps) < 3:
            random_pdps = PlatformeDematerialisation.objects.filter(
                is_published=True
            ).exclude(id=pdp.id).exclude(
                id__in=[p.id for p in similar_pdps]
            ).order_by('?')[:3-len(similar_pdps)]
            similar_pdps.extend(list(random_pdps))
        
        context['similar_pdps'] = similar_pdps
        
        # Add breadcrumb
        breadcrumb = [
            {'title': 'Plateformes de Dématérialisation', 'url': reverse('pdp_list')},
            {'title': pdp.name, 'url': None}
        ]
        context['breadcrumb_items'] = breadcrumb
        
        # Ajouter les articles liés à l'éditeur (Company)
        if pdp.company:
            context['related_articles'] = Actualites.objects.filter(
                company=pdp.company,
                is_published=True
            ).order_by('-pub_date')[:3]  # Limiter à 3 articles récents
        
        return context

class TagDetailView(ListView):
    model = Actualites
    template_name = 'news/tag_detail.html'
    context_object_name = 'actualites'
    paginate_by = 12
    
    def get_queryset(self):
        # Récupérer le tag et filtrer les actualités
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'], is_published=True)
        return Actualites.objects.filter(
            tags=self.tag,
            is_published=True
        ).order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ajouter le tag au contexte
        context['tag'] = self.tag
        
        # Ajouter les éléments du breadcrumb
        context['breadcrumb_items'] = [
            {'title': 'Actualités', 'url': reverse('actualites')},
            {'title': self.tag.name, 'url': None}
        ]
        
        return context

class PDPSpecialtyDetailView(ListView):
    model = PlatformeDematerialisation
    template_name = 'pdp/pdp_specialty_detail.html'
    context_object_name = 'pdps'
    paginate_by = 12
    
    def get_queryset(self):
        # Get the specialty slug from URL
        self.specialty_slug = self.kwargs['slug']
        
        # Try to get the specialty tag object
        try:
            from .models import PDPSpecialtyTag
            self.specialty_tag = PDPSpecialtyTag.objects.get(slug=self.specialty_slug, is_published=True)
            specialty_name = self.specialty_tag.name
        except PDPSpecialtyTag.DoesNotExist:
            # If no specialty tag exists, use the slug as the specialty name
            self.specialty_tag = None
            specialty_name = self.specialty_slug.replace('-', ' ')
        
        # Filter PDPs that contain this specialty in their specialty field
        return PlatformeDematerialisation.objects.filter(
            specialty__icontains=specialty_name,
            is_published=True
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add specialty info to context
        context['specialty_slug'] = self.specialty_slug
        context['specialty_tag'] = getattr(self, 'specialty_tag', None)
        
        # Generate specialty name for display
        if self.specialty_tag:
            context['specialty_name'] = self.specialty_tag.name
        else:
            context['specialty_name'] = self.specialty_slug.replace('-', ' ').title()
        
        # Add breadcrumb items
        context['breadcrumb_items'] = [
            {'title': 'Plateformes de Dématérialisation', 'url': reverse('pdp_list')},
            {'title': f"Spécialité {context['specialty_name']}", 'url': None}
        ]
        
        # Get all specialties for related links
        specialty_fields = PlatformeDematerialisation.objects.filter(
            is_published=True
        ).exclude(
            specialty=''
        ).values_list(
            'specialty', flat=True
        ).distinct()
        
        # Extract individual tags from comma-separated specialty fields
        all_specialties = set()
        for specialty_field in specialty_fields:
            if specialty_field:
                tags = [tag.strip() for tag in specialty_field.split(',') if tag.strip()]
                all_specialties.update(tags)
        
        # Create related specialties (exclude current one)
        current_specialty = context['specialty_name'].lower()
        related_specialties = [
            s for s in sorted(all_specialties) 
            if s.lower() != current_specialty
        ][:6]  # Limit to 6 related specialties
        
        context['related_specialties'] = related_specialties
        
        return context


def contact_software(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        entreprise = request.POST.get('entreprise')
        telephone = request.POST.get('telephone', '')
        logiciel_nom = request.POST.get('logiciel_nom')
        description = request.POST.get('description')
        use_case = request.POST.get('use_case', '')
        
        # Validation basique
        if not all([nom, email, entreprise, logiciel_nom, description]):
            messages.error(request, 'Les champs nom, email, entreprise, nom du logiciel et description sont obligatoires.')
            return render(request, 'contact_software.html')
        
        # Sauvegarde en base
        contact_obj = Contact.objects.create(
            nom=nom,
            email=email,
            entreprise=entreprise,
            message=f"""DEMANDE D'AJOUT DE LOGICIEL

Nom du logiciel: {logiciel_nom}
Téléphone: {telephone}
Cas d'usage: {use_case}

Description:
{description}"""
        )
        
        # Envoi de l'email avec logs détaillés
        try:
            logger.info(f"Tentative d'envoi d'email de demande logiciel pour {nom} ({email})")
            
            subject = f"Cabinet Digital x {entreprise} - Demande d'ajout logiciel: {logiciel_nom}"
            email_message = f"""
DE : {nom} ({email})

LOGICIEL PROPOSÉ : {logiciel_nom}
TÉLÉPHONE : {telephone}
CAS D'USAGE : {use_case}

DESCRIPTION :
{description}


DATE : {contact_obj.date_creation.strftime('%d/%m/%Y à %H:%M')}

            """
            
            logger.info(f"Envoi email de demande logiciel de '{email}' vers '{settings.DEFAULT_FROM_EMAIL}'")
            
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            logger.info("Email de demande logiciel envoyé avec succès !")
            
            # Retourner la popup pour HTMX
            return render(request, 'contact_software_success_popup.html', {'contact': contact_obj, 'logiciel_nom': logiciel_nom})
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'email de demande logiciel: {str(e)}")
            logger.error(f"Type d'erreur: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            
            # Même en cas d'erreur d'email, on affiche la popup de succès
            return render(request, 'contact_software_success_popup.html', {'contact': contact_obj, 'logiciel_nom': logiciel_nom})
    
    return render(request, 'contact_software.html')

