"""
Template tags pour l'optimisation des images
"""
from django import template
from django.utils.safestring import mark_safe
from ..utils import get_optimized_image_url, generate_responsive_image_srcset
import os

register = template.Library()

@register.simple_tag
def optimized_image(image_field, alt_text="", css_class="", width=None, height=None, loading="lazy"):
    """
    Génère une balise img optimisée avec support WebP et lazy loading
    
    Usage:
        {% optimized_image object.image "Alt text" "css-class" width=800 height=600 %}
    """
    if not image_field:
        return ""
    
    # Obtenir l'URL optimisée
    optimized_url = get_optimized_image_url(image_field)
    
    # Construire les attributs
    attributes = [
        f'src="{optimized_url}"',
        f'alt="{alt_text}"',
        f'loading="{loading}"'
    ]
    
    if css_class:
        attributes.append(f'class="{css_class}"')
    
    if width:
        attributes.append(f'width="{width}"')
    
    if height:
        attributes.append(f'height="{height}"')
    
    # Vérifier si WebP est supporté et ajouter fallback
    original_url = image_field.url
    base_url = os.path.splitext(optimized_url)[0]
    webp_url = f"{base_url}.webp"
    
    # Si c'est déjà une image WebP ou si WebP existe
    if optimized_url.endswith('.webp') or os.path.exists(image_field.path.replace(os.path.splitext(image_field.path)[1], '.webp')):
        html = f'''
        <picture>
            <source srcset="{webp_url}" type="image/webp">
            <img {' '.join(attributes)}>
        </picture>
        '''
    else:
        html = f'<img {" ".join(attributes)}>'
    
    return mark_safe(html)

@register.simple_tag
def responsive_image(image_field, alt_text="", css_class="", sizes="(max-width: 768px) 100vw, 50vw"):
    """
    Génère une image responsive avec srcset
    
    Usage:
        {% responsive_image object.image "Alt text" "css-class" %}
    """
    if not image_field:
        return ""
    
    # Obtenir l'URL optimisée
    optimized_url = get_optimized_image_url(image_field)
    
    # Générer le srcset
    srcset_data = generate_responsive_image_srcset(image_field)
    
    attributes = [
        f'src="{optimized_url}"',
        f'alt="{alt_text}"',
        'loading="lazy"'
    ]
    
    if css_class:
        attributes.append(f'class="{css_class}"')
    
    if srcset_data.get('srcset'):
        attributes.append(f'srcset="{srcset_data["srcset"]}"')
        attributes.append(f'sizes="{sizes}"')
    
    html = f'<img {" ".join(attributes)}>'
    return mark_safe(html)

@register.filter
def webp_url(image_field):
    """
    Filtre pour obtenir l'URL WebP d'une image
    
    Usage:
        {{ object.image|webp_url }}
    """
    return get_optimized_image_url(image_field)

@register.simple_tag
def image_with_fallback(image_field, alt_text="", css_class="", default_image="/static/media/default-logo.png"):
    """
    Image avec fallback en cas d'absence
    
    Usage:
        {% image_with_fallback object.image "Alt text" "css-class" %}
    """
    if image_field and hasattr(image_field, 'url'):
        return optimized_image(image_field, alt_text, css_class)
    else:
        return mark_safe(f'<img src="{default_image}" alt="{alt_text}" class="{css_class}" loading="lazy">')