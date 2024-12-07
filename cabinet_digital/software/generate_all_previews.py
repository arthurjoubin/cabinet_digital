import os
import sys
import django
from django.core.files import File

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet_digital.settings')
django.setup()

from django.conf import settings
from cabinet_digital.models import Software
from cabinet_digital.software.utils import capture_website_scroll

def generate_all_previews():
    # Créer le dossier software_previews s'il n'existe pas
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'software_previews')
    os.makedirs(preview_dir, exist_ok=True)
    
    softwares = Software.objects.filter(site__isnull=False).exclude(site='')
    
    for software in softwares:
        if software.site == "":
            print(f"Pas de site pour {software.name}")
            continue
        if software.preview_gif:
            print(f"GIF déjà généré pour {software.name}")
            continue
        print(f"Génération du GIF pour {software.name}...")
        gif_path = os.path.join(preview_dir, f'{software.slug}_preview.gif')
        
        if capture_website_scroll(software.site, gif_path):
            with open(gif_path, 'rb') as f:
                software.preview_gif.save(
                    f'{software.slug}_preview.gif',
                    File(f),
                    save=True
                )
            print(f"✓ GIF généré pour {software.name}")
        else:
            print(f"✗ Échec pour {software.name}")

if __name__ == "__main__":
    generate_all_previews()