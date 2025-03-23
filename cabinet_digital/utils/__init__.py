"""
Utility modules for the cabinet_digital project.
"""

from django.core.mail import send_mail
from django.conf import settings
import logging

def send_new_review_notification(review):
    """Envoie une notification par email lorsqu'un nouvel avis est créé"""
    logger = logging.getLogger('cabinet_digital')
    
    logger.info(f"Attempting to send email notification for review #{review.id} on {review.software.name}")
    
    subject = f'Nouvel avis sur {review.software.name}'
    message = f"""
Un nouvel avis a été créé sur Cabinet Digital:

Logiciel: {review.software.name}
Utilisateur: {review.user.userprofile.username}
Note: {review.rating}/5
Titre: {review.title}
Statut: {review.get_status_display()}

Contenu:
{review.content[:200]}...

Voir l'avis complet: https://www.cabinetdigital.fr/logiciels/{review.software.slug}/
"""
    recipient_list = ['arthurjoubin@gmail.com']
    
    # Log full email content for debugging
    logger.info("------------------------")
    logger.info("EMAIL CONTENT:")
    logger.info(f"Subject: {subject}")
    logger.info(f"From: {settings.DEFAULT_FROM_EMAIL}")
    logger.info(f"To: {', '.join(recipient_list)}")
    logger.info(f"Message: {message}")
    logger.info("------------------------")
    
    logger.info(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}, BACKEND={settings.EMAIL_BACKEND}")
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f"Email notification sent successfully for review #{review.id}")
        logger.info("If using console backend, the email should appear in the console output")
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        # Re-raise the exception if in debug mode
        if settings.DEBUG:
            raise

def test_email_system():
    """Test function to verify email sending works"""
    logger = logging.getLogger('cabinet_digital')
    logger.info("Testing email system...")
    
    subject = 'Test email from Cabinet Digital'
    message = """
Ceci est un email de test pour vérifier la configuration du système d'envoi d'emails.

Si vous recevez cet email, le système fonctionne correctement.
"""
    recipient_list = ['arthurjoubin@gmail.com']
    
    logger.info(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}, SSL={settings.EMAIL_USE_SSL}")
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info("Test email sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        # Re-raise the exception if in debug mode
        if settings.DEBUG:
            raise
        return False 