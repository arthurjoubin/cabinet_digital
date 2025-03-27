from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def cached_software_card(software_id):
    """
    Template tag that caches the rendered software card.
    """
    cache_key = f'software_card_{software_id}'
    html = cache.get(cache_key)
    
    if html is None:
        from django.template.loader import render_to_string
        from cabinet_digital.models import Software
        
        try:
            software = Software.objects.get(id=software_id)
            html = render_to_string('template_card_software.html', {'software': software})
            cache.set(cache_key, html, 3600)  # Cache for 1 hour
        except Software.DoesNotExist:
            html = ""  # Return empty string if software doesn't exist
    
    return mark_safe(html) 