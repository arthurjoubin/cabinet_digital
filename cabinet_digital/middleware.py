from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.conf import settings
from cabinet_digital.models import UserProfile
import uuid

class ProfileCompletionMiddleware:
    """
    Middleware to ensure users have completed their profile after social login.
    Redirects to the profile completion view if profile is incomplete and they're
    trying to access pages that require a complete profile.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        if request.user.is_authenticated:
            # Check if user has profile with a username
            try:
                profile = request.user.userprofile
                if not profile.username:
                    # Get current URL
                    current_url = resolve(request.path_info).url_name
                    
                    # List of URLs that don't require complete profile
                    exempt_urls = [
                        'complete_profile',
                        'logout',
                        'account_logout',
                        'admin:index',
                    ]
                    
                    # Redirect to profile completion if not in exempt URLs
                    if current_url not in exempt_urls and not request.path.startswith('/admin/'):
                        # Store the URL to redirect back to after profile completion
                        request.session['post_profile_redirect'] = request.get_full_path()
                        return redirect(reverse('complete_profile'))
            except UserProfile.DoesNotExist:
                # Créer un profil pour cet utilisateur
                UserProfile.objects.create(
                    user=request.user,
                    username=f"{request.user.email.split('@')[0]}_{uuid.uuid4().hex[:4]}"
                )
                return redirect(reverse('complete_profile'))
                
        response = self.get_response(request)
        return response 