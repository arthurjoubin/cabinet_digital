"""
Template tags pour les fils d'Ariane (breadcrumbs) avec données structurées
"""
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.inclusion_tag('partials/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, *args):
    """
    Génère un fil d'Ariane avec données structurées Schema.org
    
    Usage:
        {% breadcrumbs "Accueil" "/" "Logiciels" "/logiciels/" current_title %}
    """
    request = context['request']
    breadcrumb_items = []
    
    # Traiter les arguments par paires (nom, url)
    for i in range(0, len(args), 2):
        if i + 1 < len(args):
            name = args[i]
            url = args[i + 1]
            
            # Si c'est une URL relative, la rendre absolue
            if url and not url.startswith('http'):
                if url.startswith('/'):
                    url = request.build_absolute_uri(url)
                else:
                    url = request.build_absolute_uri('/' + url)
            
            breadcrumb_items.append({
                'name': name,
                'url': url,
                'is_current': False
            })
    
    # Le dernier élément est la page courante
    if breadcrumb_items:
        breadcrumb_items[-1]['is_current'] = True
        breadcrumb_items[-1]['url'] = None  # Pas de lien pour la page courante
    
    return {
        'breadcrumb_items': breadcrumb_items,
        'request': request
    }

@register.simple_tag(takes_context=True)
def breadcrumb_schema(context, *args):
    """
    Génère le schema JSON-LD pour les breadcrumbs
    
    Usage:
        {% breadcrumb_schema "Accueil" "/" "Logiciels" "/logiciels/" current_title %}
    """
    request = context['request']
    breadcrumb_list = []
    
    # Traiter les arguments par paires (nom, url)
    position = 1
    for i in range(0, len(args), 2):
        if i + 1 < len(args):
            name = args[i]
            url = args[i + 1]
            
            # Si c'est une URL relative, la rendre absolue
            if url and not url.startswith('http'):
                if url.startswith('/'):
                    url = request.build_absolute_uri(url)
                else:
                    url = request.build_absolute_uri('/' + url)
            
            breadcrumb_list.append({
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": url if not (i == len(args) - 2) else None  # Pas d'URL pour le dernier élément
            })
            position += 1
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_list
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')

@register.simple_tag(takes_context=True)
def auto_breadcrumbs(context):
    """
    Génère automatiquement les breadcrumbs basés sur l'URL courante
    """
    request = context['request']
    path_parts = [part for part in request.path.split('/') if part]
    
    breadcrumbs = [("Accueil", "/")]
    current_path = ""
    
    # Mapping des segments d'URL vers des noms lisibles
    url_mapping = {
        'logiciels': 'Logiciels',
        'categories': 'Catégories',  
        'integrateurs': 'Intégrateurs',
        'plateformes-dematerialisation': 'Plateformes de dématérialisation',
        'actualites': 'Actualités',
        'integrations': 'Intégrations',
        'metiers': 'Métiers'
    }
    
    for part in path_parts[:-1]:  # Exclure le dernier élément (page courante)
        current_path += f"/{part}"
        display_name = url_mapping.get(part, part.replace('-', ' ').title())
        breadcrumbs.append((display_name, current_path + "/"))
    
    # Ajouter la page courante si elle a un titre dans le contexte
    if 'page_title' in context or 'object' in context:
        if 'page_title' in context:
            current_title = context['page_title']
        elif hasattr(context.get('object'), 'name'):
            current_title = context['object'].name
        elif hasattr(context.get('object'), 'title'):
            current_title = context['object'].title
        else:
            current_title = path_parts[-1].replace('-', ' ').title() if path_parts else 'Page'
        
        breadcrumbs.append((current_title, None))
    
    return breadcrumbs