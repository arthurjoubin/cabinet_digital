import csv
import sqlite3
from django.utils.text import slugify
from django.utils.html import linebreaks
from datetime import datetime
import markdown

# Connexion à la base de données SQLite
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Ouvrir le fichier CSV
with open('cabinet_digital/management/Liste des articles.csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)

    # Lire les en-têtes
    headers = next(csv_reader)
    
    # Insérer ou mettre à jour les données
    for row in csv_reader:
        title = row[0].strip()
        slug = slugify(row[8])[:49]  # Using SEO:Slug column
        formatted_date = row[4]
        # Convertir la date du format "j/m/Y" au format "Y-m-d"
        if formatted_date == '':
            formatted_date = datetime.now().strftime('%Y-%m-%d')
        print(formatted_date)
        excerpt = row[5].strip()  # Using Excerpt column
        content = row[6].strip()  # Using Contenu column
        content_html = markdown.markdown(content)
        is_published = row[3].lower() == 'true'  # Using Publié ? column
        category = row[2].strip() if len(row) > 2 else None  # Using Catégorie column

        # Vérifier si l'entrée existe déjà
        cursor.execute('SELECT id FROM cabinet_digital_article WHERE slug = ?', (slug,))
        existing_entry = cursor.fetchone()
        
        if existing_entry:
            # Mettre à jour l'entrée existante
            cursor.execute('''
                UPDATE cabinet_digital_article 
                SET title = ?, pub_date = ?, excerpt = ?, content = ?, is_published = ?
                WHERE slug = ?
            ''', (title, formatted_date, excerpt, content_html, is_published, slug))
        else:
            # Insérer une nouvelle entrée
            cursor.execute('''
                INSERT INTO cabinet_digital_article 
                (title, slug, pub_date, excerpt, content, is_published) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, slug, formatted_date, excerpt, content_html, is_published))

# Valider les changements et fermer la connexion
conn.commit()
conn.close()

print("Importation et mise à jour des articles terminées.")