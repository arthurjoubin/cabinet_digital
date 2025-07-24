from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
import logging
from .models import Integration, Integrator, TypeIntegration, Module, ContactIntegrateur, Software

# Configuration du logger
logger = logging.getLogger(__name__)


def integration_list(request):
    integrations = Integration.objects.filter(actif=True).select_related(
        'logiciel_source', 'logiciel_destination', 'integrateur', 'type_integration'
    ).prefetch_related('modules')
    
    # Filtres
    source_id = request.GET.get('source')
    destination_id = request.GET.get('destination')
    integrateur_id = request.GET.get('integrateur')
    type_id = request.GET.get('type')
    module_id = request.GET.get('module')
    search = request.GET.get('search')
    
    if source_id:
        integrations = integrations.filter(logiciel_source_id=source_id)
    if destination_id:
        integrations = integrations.filter(logiciel_destination_id=destination_id)
    if integrateur_id:
        integrations = integrations.filter(integrateur_id=integrateur_id)
    if type_id:
        integrations = integrations.filter(type_integration_id=type_id)
    if module_id:
        integrations = integrations.filter(modules=module_id)
    if search:
        integrations = integrations.filter(
            Q(nom__icontains=search) |
            Q(description__icontains=search) |
            Q(logiciel_source__name__icontains=search) |
            Q(logiciel_destination__name__icontains=search) |
            Q(integrateur__name__icontains=search) |
            Q(modules__nom__icontains=search)
        ).distinct()
    
    # Pagination
    paginator = Paginator(integrations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Données pour les filtres
    logiciels_source = Software.objects.filter(
        integrations_source__actif=True
    ).distinct().order_by('name')
    
    logiciels_destination = Software.objects.filter(
        integrations_destination__actif=True
    ).distinct().order_by('name')
    
    integrateurs = Integrator.objects.filter(
        integrations__actif=True
    ).distinct().order_by('name')
    
    types = TypeIntegration.objects.all().order_by('nom')
    modules = Module.objects.all().order_by('ordre', 'nom')
    
    context = {
        'page_obj': page_obj,
        'logiciels_source': logiciels_source,
        'logiciels_destination': logiciels_destination,
        'integrateurs': integrateurs,
        'types': types,
        'modules': modules,
        'filters': {
            'source': source_id,
            'destination': destination_id,
            'integrateur': integrateur_id,
            'type': type_id,
            'module': module_id,
            'search': search,
        }
    }
    
    return render(request, 'integrations/integration_list.html', context)


def integration_detail(request, slug):
    integration = get_object_or_404(
        Integration.objects.select_related(
            'logiciel_source', 'logiciel_destination', 'integrateur', 'type_integration'
        ).prefetch_related('modules'),
        slug=slug,
        actif=True
    )
    
    # Autres intégrations similaires
    similar = Integration.objects.filter(
        Q(logiciel_source=integration.logiciel_source) |
        Q(logiciel_destination=integration.logiciel_destination) |
        Q(modules__in=integration.modules.all())
    ).exclude(id=integration.id).filter(actif=True).select_related(
        'logiciel_source', 'logiciel_destination', 'integrateur'
    ).distinct()[:6]
    
    context = {
        'integration': integration,
        'similar': similar,
    }
    
    return render(request, 'integrations/integration_detail.html', context)


def integrateur_detail(request, slug):
    integrateur = get_object_or_404(Integrator, slug=slug, is_published=True)
    integrations = integrateur.integrations.filter(actif=True).select_related(
        'logiciel_source', 'logiciel_destination', 'type_integration'
    ).prefetch_related('modules')
    
    context = {
        'integrateur': integrateur,
        'integrations': integrations,
    }
    
    return render(request, 'integrations/integrateur_detail.html', context)


def contact_integration(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        entreprise = request.POST.get('entreprise')
        logiciel_source = request.POST.get('logiciel_source')
        logiciel_destination = request.POST.get('logiciel_destination')
        modules_concernes = request.POST.get('modules_concernes')
        description = request.POST.get('description')
        url_documentation = request.POST.get('url_documentation', '')
        
        # Validation basique
        if not all([nom, email, entreprise, logiciel_source, logiciel_destination, modules_concernes, description]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return render(request, 'integrations/contact_integrateur.html')
        
        # Sauvegarde en base
        contact = ContactIntegrateur.objects.create(
            nom=nom,
            email=email,
            entreprise=entreprise,
            type_contact='integrateur',  # Valeur par défaut
            logiciel_source=logiciel_source,
            logiciel_destination=logiciel_destination,
            modules_concernes=modules_concernes,
            description=description,
            url_documentation=url_documentation,
            telephone=''  # Champ vide
        )
        
        # Envoi de l'email avec logs détaillés
        try:
            logger.info(f"Tentative d'envoi d'email pour {nom} ({email})")
            logger.info(f"Configuration email: Host={settings.EMAIL_HOST}, Port={settings.EMAIL_PORT}, User={settings.EMAIL_HOST_USER}")
            
            subject = f"Cabinet Digital x {entreprise} - Demande d'intégration logiciel"
            message = f"""
DE : {nom} ({email})

LOGICIEL SOURCE : {logiciel_source}
LOGICIEL DESTINATION : {logiciel_destination}
MODULES CONCERNÉS : {modules_concernes}
DOCUMENTATION : {url_documentation or 'Non renseignée'}

DESCRIPTION :
{description}


DATE : {contact.date_creation.strftime('%d/%m/%Y à %H:%M')}

            """
            
            logger.info(f"Envoi email de '{settings.DEFAULT_FROM_EMAIL}' vers '{settings.DEFAULT_FROM_EMAIL}'")
            logger.info(f"Sujet: {subject}")
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Vous recevrez l'email
                fail_silently=False,
            )
            
            logger.info("Email envoyé avec succès !")
            
            # Retourner la popup pour HTMX
            return render(request, 'integrations/contact_success_popup.html', {'contact': contact})
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'email: {str(e)}")
            logger.error(f"Type d'erreur: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            
            # Même en cas d'erreur d'email, on affiche la popup de succès
            # car la demande est sauvegardée en base
            return render(request, 'integrations/contact_success_popup.html', {'contact': contact})
    
    return render(request, 'integrations/contact_integrateur.html')


def test_email(request):
    """Vue de test pour vérifier l'envoi d'email"""
    if not settings.DEBUG:
        return HttpResponse("Test uniquement en mode DEBUG", status=403)
    
    try:
        logger.info("=== TEST EMAIL ===")
        logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        logger.info(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        from django.core.mail import get_connection
        connection = get_connection()
        logger.info(f"Connection créée: {connection}")
        
        send_mail(
            'Test Email Cabinet Digital',
            'Ceci est un email de test pour vérifier la configuration SMTP.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        logger.info("Email de test envoyé avec succès!")
        return HttpResponse("Email de test envoyé avec succès! Vérifiez votre boîte mail et les logs.")
        
    except Exception as e:
        logger.error(f"Erreur lors du test email: {str(e)}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback complet: {traceback.format_exc()}")
        return HttpResponse(f"Erreur: {str(e)}", status=500)


 