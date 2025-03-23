from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Software, SoftwareCategory, Actualites, Tag, Metier, AIModel, AITool, AIArticle, AIToolCategory, ProviderAI, UserProfile, Review, ReviewImage, ReviewVote
from django.conf import settings
from django.db.models import Count, Prefetch, Q, F
from django.shortcuts import redirect
from django.utils.text import slugify
from django.db.models.functions import Lower
from django.http import JsonResponse
import logging
from django.template.loader import get_template
from django.shortcuts import render
from datetime import date
import unidecode
from urllib.parse import unquote
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    View, TemplateView, FormView, UpdateView, DeleteView, CreateView
)
from django.http import HttpResponseForbidden
from django.utils import timezone
import json
from django.contrib import messages
from django.db import transaction
import uuid
from django import forms


logger = logging.getLogger(__name__)

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

def home(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')



class CategoryListView(ListView):
    model = SoftwareCategory
    template_name = 'category_list.html'
    context_object_name = 'categories'
    def get_queryset(self):
        queryset = SoftwareCategory.objects.annotate(
            software_count=Count('categories_softwares_link')
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
        return context

class SoftwareListView(ListView):
    model = Software
    template_name = 'software_list.html'
    context_object_name = 'softwares'
    paginate_by = 12

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['template_card_software_list_partial.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SoftwareCategory.objects.annotate(
            software_count=Count('categories_softwares_link')
        ).order_by(Lower('name'))
        context['selected_category'] = self.request.GET.get('categorie')
        context['search_query'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', 'alpha')
        context['metiers'] = Metier.objects.all().order_by('name')
        context['selected_metier'] = self.request.GET.get('metier')
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-is_top_pick', Lower('name'))
        queryset = queryset.filter(is_published=True, slug__isnull=False).exclude(slug='')
        category = self.request.GET.get('categorie')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort')
        metier = self.request.GET.get('metier')

        # Apply sorting
        if sort == 'views':
            queryset = queryset.order_by('-unique_views')
        elif sort == 'alpha':
            queryset = queryset.order_by('name')

        if category and category != 'None':
            queryset = queryset.filter(category__slug=category)
        if metier and metier != 'None':
            queryset = queryset.filter(Q(metier__slug=metier) | Q(category__metier__slug=metier))
        if search and search.strip():
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        return queryset

class ActualitesListView(ListView):
    model = Actualites
    template_name = 'actualites.html'
    context_object_name = 'actualites'

    def get_queryset(self):
        return Actualites.objects.filter(is_published=True).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
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
        return (
            Software.objects
            .prefetch_related(
                Prefetch('category', queryset=SoftwareCategory.objects.only('name', 'slug'))
            )
            .select_related('metier')
            .only('name', 'description', 'slug', 'unique_views', 'is_top_pick', 'metier__name')
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        viewed_softwares = self.request.session.get('viewed_softwares', [])
        
        # On ne compte que sur une requête de chargement complet et si ce n'est pas un robot
        if not self.request.headers.get('HX-Request') and obj.id not in viewed_softwares and not self.request.user_agent.is_bot:
            Software.objects.filter(id=obj.id).update(unique_views=F('unique_views') + 1)
            
            obj.refresh_from_db()
            
            viewed_softwares.append(obj.id)
            self.request.session['viewed_softwares'] = viewed_softwares
            
            self.request.session.set_expiry(86400)  # 24 heures en secondes
        
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        software = self.object
        categories = software.category.all()

        similar_softwares = (
            Software.objects
            .filter(
                is_published=True,
                category__in=categories,
            )
            .exclude(id=software.id)
            .prefetch_related(
                Prefetch('category', queryset=SoftwareCategory.objects.only('name', 'slug'))
            )
            .only('name', 'slug', 'is_top_pick')
            .distinct()
            .annotate(
                common_categories=Count(
                    'category',
                    filter=Q(category__in=categories)
                )
            )
            .order_by('-common_categories', '-is_top_pick')[:3]
        )
        
        # Get published reviews
        reviews = Review.objects.filter(
            software=software,
            status='published'
        ).select_related(
            'user__userprofile'
        ).prefetch_related(
            'images',
            'votes'
        ).order_by('-publish_date')
        
        # Pagination for reviews
        paginator = Paginator(reviews, 5)  # 5 reviews per page
        page_number = self.request.GET.get('page')
        reviews_page = paginator.get_page(page_number)
        
        # Check if user has already submitted a review
        user_has_review = False
        user_review = None
        if self.request.user.is_authenticated:
            try:
                user_review = Review.objects.get(
                    user=self.request.user,
                    software=software
                )
                user_has_review = True
            except Review.DoesNotExist:
                pass
        
        # Add review data to context
        context.update({
            'similar_softwares': similar_softwares,
            'days_since': (date.today() - date(2024, 11, 10)).days,
            'reviews': reviews_page,
            'user_has_review': user_has_review,
            'user_review': user_review,
            'review_count': reviews.count(),
            'average_rating': software.average_rating(),
            'star_rating': software.get_star_rating(),
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
        
    # Si pas de redirection spécifique, utiliser le mapping général
    path_mapping = {
        'solution': 'logiciels',
        'news': 'actualites', 
        'article': 'articles',
        'categorie': 'categories'
    }
    new_path = path_mapping.get(old_path, old_path)
    
    # Construire l'URL de redirection
    redirect_url = f'/{new_path}/{slug}/'
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
            
            # Générer la commande de planification si nécessaire
            schedule_command = ''
            if data['schedule_type'] != 'none':
                schedule_command = generate_schedule_command(data)  # data est maintenant passé correctement
            
            response_data = {
                'script': script_content,
                'schedule_command': schedule_command
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Erreur dans la génération du script SFTP : {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'outils/sftp_generator.html')

def amortissement_calculateur(request):
    return render(request, 'outils/amortissement_calculateur.html')

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
    }
    
    return render(request, 'actualites.html', context)

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
        
        # Ne pas incrémenter le compteur si c'est un robot
        if not self.request.user_agent.is_bot:
            obj.unique_views += 1
            obj.save()
        
        return obj

class AIToolListView(ListView):
    model = AITool
    template_name = 'ai/tool_list.html'
    context_object_name = 'tools'
    paginate_by = 12

    def get_queryset(self):
        queryset = AITool.objects.filter(is_published=True)
        return queryset.distinct().order_by('-is_top_pick', Lower('name'))

class AIToolDetailView(DetailView):
    model = AITool
    template_name = 'ai/tool_detail.html'
    context_object_name = 'tool'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get('slug')
        decoded_slug = unidecode.unidecode(slug)
        clean_slug = slugify(decoded_slug)[:49]
        
        obj = get_object_or_404(queryset, slug=clean_slug, is_published=True)
        
        # Ne pas incrémenter le compteur si c'est un robot
        if not self.request.user_agent.is_bot:
            obj.unique_views += 1
            obj.save()
        
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
    template_name = 'metier_detail.html'
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
        context['categories'] = SoftwareCategory.objects.filter(
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
        ).distinct().order_by('-is_top_pick', 'name')
        
        # Pagination des logiciels
        paginator = Paginator(softwares, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['softwares'] = page_obj
        context['page_obj'] = page_obj
        
        return context

class CompleteProfileView(LoginRequiredMixin, FormView):
    template_name = 'profile/complete_profile.html'
    success_url = reverse_lazy('user_reviews')
    
    class ProfileForm(forms.ModelForm):
        class Meta:
            model = UserProfile
            fields = ['username']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'})
            }
            labels = {
                'username': 'Nom d\'affichage'
            }
            help_texts = {
                'username': 'Ce nom sera visible publiquement avec vos avis et commentaires.'
            }
    
    form_class = ProfileForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.userprofile
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Votre profil a été complété avec succès.")
        return super().form_valid(form)
    
    def get_success_url(self):
        # Rediriger vers l'URL stockée en session ou vers la page d'avis par défaut
        next_url = self.request.session.pop('post_profile_redirect', None)
        if next_url:
            return next_url
        return reverse('user_reviews')


class UserProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'profile/user_profile.html'
    success_url = reverse_lazy('user_profile')
    
    class ProfileForm(forms.ModelForm):
        class Meta:
            model = UserProfile
            fields = ['username']
            widgets = {
                'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'})
            }
    
    form_class = ProfileForm
    
    def get_object(self):
        return self.request.user.userprofile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_count'] = Review.objects.filter(user=self.request.user).count()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Votre profil a été mis à jour avec succès.")
        return super().form_valid(form)


class UserReviewsView(LoginRequiredMixin, ListView):
    template_name = 'profile/user_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Review.objects.filter(user=self.request.user).order_by('-created_at')
        # Handle filtering
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter in ['draft', 'pending', 'published', 'rejected']:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter counts
        context['draft_count'] = Review.objects.filter(user=self.request.user, status='draft').count()
        context['pending_count'] = Review.objects.filter(user=self.request.user, status='pending').count()
        context['published_count'] = Review.objects.filter(user=self.request.user, status='published').count()
        context['rejected_count'] = Review.objects.filter(user=self.request.user, status='rejected').count()
        
        # Set active filter
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter in ['draft', 'pending', 'published', 'rejected']:
            context['active_filter'] = status_filter
        else:
            context['active_filter'] = 'all'
            
        return context


# Custom widget for multiple file upload
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs'].update({
            'accept': 'image/jpeg,image/png,image/webp,image/gif',
            'class': 'w-full p-2 border-0 rounded-md',
            'multiple': True
        })
        return context

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)
        
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = 'reviews/review_form.html'
    
    class ReviewForm(forms.ModelForm):
        images = MultipleFileField(required=False)
        
        class Meta:
            model = Review
            fields = ['title', 'content', 'rating']
            widgets = {
                'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
                'content': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'rows': 6}),
                'rating': forms.RadioSelect()
            }
    
    form_class = ReviewForm
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user already has a review for this software
        software = get_object_or_404(Software, slug=self.kwargs['slug'])
        if Review.objects.filter(user=request.user, software=software).exists():
            messages.error(request, "Vous avez déjà publié un avis pour ce logiciel. Vous pouvez modifier votre avis existant.")
            return redirect('software_detail', slug=software.slug)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        # Redirect to the software detail page
        return reverse('software_detail', kwargs={'slug': self.kwargs['slug']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['software'] = get_object_or_404(Software, slug=self.kwargs['slug'])
        context['max_images'] = settings.MAX_REVIEW_IMAGES
        return context
    
    def form_valid(self, form):
        # Get software from URL
        software = get_object_or_404(Software, slug=self.kwargs['slug'])
        
        # Check if user already has a review for this software
        if Review.objects.filter(user=self.request.user, software=software).exists():
            messages.error(self.request, "Vous avez déjà publié un avis pour ce logiciel.")
            return redirect('software_detail', slug=software.slug)
        
        # Set additional fields
        form.instance.user = self.request.user
        form.instance.software = software
        
        # Set status based on submit button
        submit_action = self.request.POST.get('submit_action', 'draft')
        if submit_action == 'submit':
            form.instance.status = 'pending'
        else:
            form.instance.status = 'draft'
        
        # Save the review
        with transaction.atomic():
            response = super().form_valid(form)
            
            # Process images
            images = self.request.FILES.getlist('images')
            for i, image in enumerate(images[:settings.MAX_REVIEW_IMAGES]):
                # Create the image
                review_image = ReviewImage(
                    review=self.object,
                    image=image,
                    order=i
                )
                review_image.save()
        
        # Add success message
        if form.instance.status == 'pending':
            messages.success(self.request, "Votre avis a été soumis et est en attente de validation.")
        else:
            messages.success(self.request, "Votre avis a été enregistré comme brouillon.")
        
        return response


class ReviewEditView(LoginRequiredMixin, UpdateView):
    model = Review
    template_name = 'reviews/review_form.html'
    
    class ReviewForm(forms.ModelForm):
        images = MultipleFileField(required=False)
        
        class Meta:
            model = Review
            fields = ['title', 'content', 'rating']
            widgets = {
                'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
                'content': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'rows': 6}),
                'rating': forms.RadioSelect()
            }
    
    form_class = ReviewForm
    
    def get_success_url(self):
        return reverse('software_detail', kwargs={'slug': self.kwargs['slug']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['software'] = get_object_or_404(Software, slug=self.kwargs['slug'])
        context['existing_images'] = self.object.images.all()
        context['max_images'] = settings.MAX_REVIEW_IMAGES
        context['is_edit'] = True
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is the owner of the review
        review = self.get_object()
        if review.user != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à modifier cet avis.")
            return redirect('software_detail', slug=self.kwargs['slug'])
        
        # Check if the review can be edited (within 24h window if published)
        if review.status == 'published' and not review.can_be_edited():
            messages.error(request, "Cet avis ne peut plus être modifié car il a été publié il y a plus de 24 heures.")
            return redirect('software_detail', slug=self.kwargs['slug'])
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Process images to be deleted
        images_to_delete = self.request.POST.getlist('delete_image')
        
        # Set status based on submit button
        submit_action = self.request.POST.get('submit_action', 'update')
        old_status = self.object.status
        
        if submit_action == 'submit' and old_status == 'draft':
            form.instance.status = 'pending'
        
        # Save the review
        with transaction.atomic():
            # Delete images marked for deletion
            for image_id in images_to_delete:
                try:
                    image = ReviewImage.objects.get(id=image_id, review=self.object)
                    image.delete()
                except ReviewImage.DoesNotExist:
                    pass
            
            # Process new images
            current_image_count = self.object.images.count()
            new_images = self.request.FILES.getlist('images')
            available_slots = settings.MAX_REVIEW_IMAGES - current_image_count + len(images_to_delete)
            
            for i, image in enumerate(new_images[:available_slots]):
                # Create the image
                review_image = ReviewImage(
                    review=self.object,
                    image=image,
                    order=current_image_count + i
                )
                review_image.save()
            
            response = super().form_valid(form)
        
        # Add success message
        if old_status == 'draft' and form.instance.status == 'pending':
            messages.success(self.request, "Votre avis a été soumis et est en attente de validation.")
        else:
            messages.success(self.request, "Votre avis a été mis à jour avec succès.")
        
        return response


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'reviews/review_confirm_delete.html'
    
    def get_success_url(self):
        if self.request.GET.get('next') == 'profile':
            return reverse('user_reviews')
        return reverse('software_detail', kwargs={'slug': self.kwargs['slug']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['software'] = self.object.software
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is the owner of the review
        review = self.get_object()
        if review.user != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à supprimer cet avis.")
            return redirect('software_detail', slug=self.kwargs['slug'])
        
        return super().dispatch(request, *args, **kwargs)


class ReviewVoteView(LoginRequiredMixin, View):
    """Handle AJAX voting on reviews"""
    
    def post(self, request, *args, **kwargs):
        review_id = self.kwargs.get('pk')
        review = get_object_or_404(Review, id=review_id, status='published')
        
        # Check if user is not voting on their own review
        if review.user == request.user:
            return JsonResponse({
                'success': False,
                'message': "Vous ne pouvez pas voter sur votre propre avis."
            }, status=403)
        
        # Get vote data from request
        try:
            data = json.loads(request.body)
            vote_value = data.get('vote')
            
            if vote_value not in [1, -1]:
                raise ValueError("Vote value must be 1 or -1")
                
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        
        # Process vote
        try:
            # Check if user already voted
            vote, created = ReviewVote.objects.get_or_create(
                user=request.user,
                review=review,
                defaults={'vote': vote_value}
            )
            
            if not created:
                # If same vote, remove it (toggle)
                if vote.vote == vote_value:
                    vote.delete()
                    action = 'removed'
                else:
                    # If different vote, update it
                    vote.vote = vote_value
                    vote.save()
                    action = 'changed'
            else:
                action = 'added'
            
            # Return updated counts
            return JsonResponse({
                'success': True,
                'action': action,
                'upvotes': review.upvotes(),
                'downvotes': review.downvotes(),
                'score': review.vote_score()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)


def post_social_login(request):
    """
    Vue appelée après une connexion sociale réussie.
    Vérifie si l'utilisateur a un profil complet, sinon le redirige vers la page de complétion de profil.
    """
    # Vérifier si c'est la première connexion de l'utilisateur
    first_login = False
    
    # Vérifier si l'utilisateur a un profil utilisateur
    if not hasattr(request.user, 'userprofile'):
        from cabinet_digital.models import UserProfile
        # Créer un profil utilisateur vide
        UserProfile.objects.create(user=request.user)
        first_login = True
    
    # Vérifier si le profil est complet (a un nom d'utilisateur)
    if not request.user.userprofile.username:
        # Stocker l'URL de redirection après complétion du profil
        next_url = request.GET.get('next')
        if next_url:
            request.session['post_profile_redirect'] = next_url
        
        # Ajouter un message encourageant la modification du nom d'affichage
        if first_login:
            messages.info(request, "Bienvenue ! Pour une meilleure expérience, veuillez choisir un nom d'affichage qui sera visible dans vos avis et commentaires.")
        else:
            messages.info(request, "Veuillez compléter votre profil en ajoutant un nom d'affichage pour pouvoir publier des avis.")
        
        return redirect('complete_profile')
    
    # Rediriger vers la page demandée ou vers "Mes avis" par défaut
    next_url = request.GET.get('next', reverse('user_reviews'))
    return redirect(next_url)
