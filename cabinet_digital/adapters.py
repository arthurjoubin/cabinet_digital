from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse

class NoSignupAccountAdapter(DefaultAccountAdapter):
    """
    Adaptateur qui empêche l'inscription directe et redirige vers la page d'accueil
    """
    def is_open_for_signup(self, request):
        """
        Désactiver l'inscription directe par email/mot de passe
        """
        return False
    
    def get_login_redirect_url(self, request):
        """
        Rediriger vers la page d'accueil après connexion
        """
        return reverse('home')

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptateur personnalisé pour la gestion des comptes sociaux
    """
    def is_open_for_signup(self, request, sociallogin):
        """
        Autoriser l'inscription via comptes sociaux
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Personnaliser les données utilisateur lors de l'inscription
        """
        user = super().populate_user(request, sociallogin, data)
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Rediriger vers la page d'accueil après connexion sociale
        """
        return reverse('home') 