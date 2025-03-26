from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse
import uuid

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
        
        # Ajouter un facteur aléatoire pour éviter les conflits de noms d'utilisateur
        if data.get('email'):
            username_base = data['email'].split('@')[0]
            user.username = f"{username_base}_{uuid.uuid4().hex[:8]}"
        
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Rediriger vers la page d'accueil après connexion sociale
        """
        return reverse('home') 