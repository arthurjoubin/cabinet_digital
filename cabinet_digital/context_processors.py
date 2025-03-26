from .models import SoftwareCategory
from django.db.models import Count

def categories_processor(request):
    categories = SoftwareCategory.objects.annotate(
        software_count=Count('categories_softwares_link')
    ).filter(software_count__gt=0, is_published=True).order_by('name')
    
    return {
        'categories': categories
    } 