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
with open('cabinet_digital/management/Liste des news marché md.csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)

    # Ignorer l'en-tête si nécessaire
    next(csv_reader, None)
    
    # Insérer ou mettre à jour les données
    for row in csv_reader:
        # Convertir le contenu Markdown en HTML
        content_html = markdown.markdown(row[6])

        title = row[5].replace('*', '').strip()
        slug = slugify(row[11])[:49]  # SEO:Slug

        
        # Vérifier si l'entrée existe déjà
        cursor.execute('SELECT id FROM cabinet_digital_news WHERE slug = ?', (slug,))
        existing_entry = cursor.fetchone()
        
        if existing_entry:
            # Mettre à jour l'entrée existante
            cursor.execute('''
                UPDATE cabinet_digital_news 
                SET title = ?, date = ?, excerpt = ?, content = ?, is_published = ?
                WHERE slug = ?
            ''', (
                title,
                row[2],  # Date (déjà formatée)
                row[8],  # Excerpt
                content_html,  # Contenu (déjà formaté)
                True,  # Publié ? (converti en booléen)
                slug
            ))
        else:
            # Insérer une nouvelle entrée
            cursor.execute('''
                INSERT INTO cabinet_digital_news 
                (title, slug, date, excerpt, content, is_published) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                title,
                slug,
                row[2],  # Date (déjà formatée)
                row[8],  # Excerpt
                content_html,  # Contenu (déjà formaté)
                True  # Publié ? (converti en booléen)
            ))

# Valider les changements et fermer la connexion
conn.commit()
conn.close()

print("Importation et mise à jour terminées.")