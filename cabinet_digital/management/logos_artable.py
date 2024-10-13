import requests
import os
from PIL import Image
import io
from django.utils.text import slugify
import logging
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = 'patXfgNVP6roolijg.dc5336a4ccf7ad74a6a16819c802436a1da3fbd648eb2bed2f84feee3a7b5587'
BASE_ID = 'appOsLjDFcICB05w6'
TABLE_NAME = 'Liste des logiciels'
LOGO_FIELD = 'Logo'
SOLUTION_FIELD = 'Solution'

def get_all_records():
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {'pageSize': 100}  # Spécifier explicitement la taille de la page
    
    all_records = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        all_records.extend(data.get('records', []))
        logging.info(f"Récupéré {len(all_records)} enregistrements jusqu'à présent")
        
        if 'offset' in data:
            params['offset'] = data['offset']
        else:
            break
    
    return all_records

records = get_all_records()
logging.info(f"Nombre total d'enregistrements récupérés d'Airtable : {len(records)}")

os.makedirs('logos_comprimes', exist_ok=True)

successful_downloads = 0
failed_downloads = 0
no_logo_count = 0
processed_records = 0
missing_fields = 0
already_exists_count = 0

for record in records:
    processed_records += 1
    fields = record.get('fields', {})
    
    if SOLUTION_FIELD not in fields or LOGO_FIELD not in fields:
        logging.warning(f"Record {processed_records}: Champs manquants. SOLUTION_FIELD: {SOLUTION_FIELD in fields}, LOGO_FIELD: {LOGO_FIELD in fields}")
        missing_fields += 1
        continue
    
    solution_name = fields.get(SOLUTION_FIELD, 'unknown')
    solution_slug = slugify(solution_name).replace('-', '_')
    
    logging.info(f"Traitement de la solution : {solution_name} (slug: {solution_slug})")
    
    if not fields[LOGO_FIELD]:
        logging.warning(f"Pas de logo pour la solution {solution_name}")
        no_logo_count += 1
        continue
    
    output_path = f'cabinet_digital/management/logos_comprimes/{solution_slug}.webp'
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(output_path):
        logging.info(f'Le logo pour {solution_name} existe déjà. Pas besoin de le télécharger à nouveau.')
        already_exists_count += 1
        continue
    
    image_url = fields[LOGO_FIELD][0]['url']
    logging.info(f"URL du logo trouvée : {image_url}")
    
    try:
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()
        
        img = Image.open(io.BytesIO(image_response.content))
        
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            logging.warning(f"Format d'image non pris en charge pour {solution_name}: {img.format}")
            failed_downloads += 1
            continue
        
        img.thumbnail((300, 300))
        
        img.save(output_path, 'WEBP', quality=85, lossless=True)
        
        logging.info(f'Logo compressé et ajouté au répertoire : {solution_slug}.webp')
        successful_downloads += 1
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors du téléchargement de {solution_name}: {str(e)}")
        failed_downloads += 1
    except Exception as e:
        logging.error(f"Erreur lors du traitement de {solution_name}: {str(e)}")
        failed_downloads += 1

logging.info("Traitement terminé")

# Vérification finale
logos_dir = 'cabinet_digital/management/logos_comprimes'
logos_files = os.listdir(logos_dir)
logging.info(f"Nombre total de logos téléchargés : {len(logos_files)}")
logging.info(f"Téléchargements réussis : {successful_downloads}")
logging.info(f"Téléchargements échoués : {failed_downloads}")
logging.info(f"Solutions sans logo : {no_logo_count}")
logging.info(f"Records traités : {processed_records}")
logging.info(f"Records avec champs manquants : {missing_fields}")
logging.info(f"Logos déjà existants : {already_exists_count}")

# Sauvegarde des données pour analyse
with open('airtable_data.json', 'w') as f:
    json.dump(records, f, indent=2)

logging.info("Données Airtable sauvegardées dans airtable_data.json pour analyse")

# Vérification des slugs générés
all_slugs = [slugify(r['fields'].get(SOLUTION_FIELD, '')).replace('-', '_') for r in records]
logging.info(f"Tous les slugs générés : {', '.join(all_slugs)}")
