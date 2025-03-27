from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger('cabinet_digital')

class ProfileCompletionMiddleware:
    """
    Middleware that redirects users to the profile completion page
    if they haven't completed their profile yet.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Désactiver temporairement la redirection
        return self.get_response(request)
        
        # Code original commenté ci-dessous
        """
        # Skip checks if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check if user has a profile
        if not hasattr(request.user, 'userprofile'):
            return self.get_response(request)
            
        # Admin users can bypass
        if request.user.is_staff:
            return self.get_response(request)
        
        # Skip middleware for excluded paths
        excluded_paths = [
            '/complete-profile/',
            '/accounts/logout/',
            '/static/',
            '/media/',
            '/api/',
            '/user/profile/update/',
            '/admin',
        ]
        
        # Check if the current path is excluded
        current_path = request.path_info
        for path in excluded_paths:
            if current_path.startswith(path):
                return self.get_response(request)
                
        # Check if profile is incomplete
        profile = request.user.userprofile
        
        # Check if username is temporary - needs to be set by user
        if profile.username.find('_') > 0:
            # Temporary username detected
            # If we're not on the complete_profile page, redirect there
            if current_path != reverse('complete_profile'):
                return redirect('complete_profile')
        """    
        # response = self.get_response(request)
        # return response

class AnonymousUserCacheMiddleware:
    """
    Middleware that skips cache middleware if the user is authenticated.
    Must be placed before the UpdateCacheMiddleware and after the FetchFromCacheMiddleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip cache for authenticated users
        if request.user.is_authenticated:
            request._cache_update_cache = False

        response = self.get_response(request)
        return response 