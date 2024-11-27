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
from django.http import HttpResponse
import json
from django.http import JsonResponse
import logging
from django.template.loader import get_template
from logging.handlers import RotatingFileHandler
import shutil

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
                category__in=categories,
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
            .order_by('-common_categories').order_by('-is_top_pick')[:4]
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
        template = get_template('roi_calculateur.html')
        logger.info(f"Template trouvé : {template.origin.name}")
        logger.info(f"Template dirs : {settings.TEMPLATES[0]['DIRS']}")
        logger.info("Tentative de rendu du template roi_calculateur.html")
        response = render(request, 'roi_calculateur.html')
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
    
    return render(request, 'immobilier_calculateur.html')

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
    
    return render(request, 'sftp_generator.html')