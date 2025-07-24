from django import template
import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_value(obj, attr):
    """Get an attribute value from an object."""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif hasattr(obj, 'get') and callable(obj.get):
        return obj.get(attr, '')
    elif attr in obj:
        return obj[attr]
    return ''

@register.filter
def markdown_to_html(value):
    """Convert markdown text to HTML."""
    if not value:
        return ''
    
    # Configure markdown with extensions for better formatting
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
    ])
    
    html = md.convert(value)
    return mark_safe(html)

@register.filter
def published_only(queryset):
    """Filter queryset to only include published items."""
    if hasattr(queryset, 'filter'):
        return queryset.filter(is_published=True)
    return queryset 