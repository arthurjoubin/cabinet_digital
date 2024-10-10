import csv
import sqlite3
from django.utils.text import slugify
from django.utils.html import linebreaks
from datetime import datetime

# Connexion à la base de données SQLite
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Ouvrir le fichier CSV
with open('cabinet_digital/management/Liste des news marché.csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)

    # Ignorer l'en-tête si nécessaire
    next(csv_reader, None)
    
    # Insérer les données
    for row in csv_reader:
        # Convertir le contenu en HTML avec des sauts de ligne
        content_with_linebreaks = linebreaks(row[2])
        
        # Convertir la date du format "j/m/Y" au format "Y-m-d"
        date_obj = datetime.strptime(row[5], '%d/%m/%Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        
        # Assurez-vous que le nombre de ? correspond au nombre de colonnes dans votre table
        cursor.execute('''
            INSERT INTO cabinet_digital_news 
            (title,slug,date,excerpt,content, is_published) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row[1], slugify(row[6])[:49], formatted_date, row[3], content_with_linebreaks, True))

# Valider les changements et fermer la connexion
conn.commit()
conn.close()

print("Importation terminée.")