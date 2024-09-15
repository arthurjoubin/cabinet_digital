import csv
import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Ouvrir le fichier CSV
with open(r'C:\Users\arthu\OneDrive\Bureau\cabinet_digital\media\import_histo\Liste des articles-Export (4).csv', 'r', encoding='utf-8') as f:
    csv_reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
    
    # Ignorer l'en-tête si nécessaire
    next(csv_reader, None)
    
    # Insérer les données
    for row in csv_reader:
        # Assurez-vous que le nombre de ? correspond au nombre de colonnes dans votre table
        cursor.execute('''
            INSERT INTO cabinet_digital_article 
            (title,slug,pub_date,excerpt,content) 
            VALUES (?, ?, ?, ?,?)
        ''', row)

# Valider les changements et fermer la connexion
conn.commit()
conn.close()

print("Importation terminée.")