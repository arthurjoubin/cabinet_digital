from .models import SoftwareCategory
from django.db.models import Count
from django.core.cache import cache

def categories_processor(request):
    # Retrieve from cache with a 1-hour duration
    categories = cache.get('header_categories')
    
    if categories is None:
        categories = SoftwareCategory.objects.annotate(
            software_count=Count('categories_softwares_link')
        ).filter(software_count__gt=0, is_published=True).order_by('name')
        
        # Store in cache for 1 hour (3600 seconds)
        cache.set('header_categories', categories, 3600)
    
    return {
        'categories': categories
    } 