from django.core.management.base import BaseCommand
from cabinet_digital.models import Software
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Export unpublished software with AI research prompt'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'txt'],
            default='txt',
            help='Output format (json or txt)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='unpublished_software',
            help='Output filename (without extension)'
        )

    def handle(self, *args, **options):
        # Get unpublished software
        unpublished_software = Software.objects.filter(is_published=False).order_by('name')
        
        if not unpublished_software.exists():
            self.stdout.write(
                self.style.WARNING('Aucun logiciel non publié trouvé.')
            )
            return

        software_list = []
        for software in unpublished_software:
            software_data = {
                'name': software.name,
                'slug': software.slug,
                'current_description': software.description,
                'excerpt': software.excerpt,
                'site': software.site,
                'categories': [cat.name for cat in software.category.all()],
                'metier': software.metier.name if software.metier else None,
                'company': software.company.name if software.company else None,
            }
            software_list.append(software_data)

        # Generate AI research prompt
        ai_prompt = self._generate_ai_prompt(software_list)
        
        # Export based on format
        if options['format'] == 'json':
            self._export_json(software_list, ai_prompt, options['output'])
        else:
            self._export_txt(software_list, ai_prompt, options['output'])

        self.stdout.write(
            self.style.SUCCESS(
                f'Export terminé: {len(software_list)} logiciels non publiés exportés vers {options["output"]}.{options["format"]}'
            )
        )

    def _generate_ai_prompt(self, software_list):
        prompt = """# PROMPT DE RECHERCHE IA POUR LOGICIELS NON PUBLIÉS

## CONTEXTE
Vous êtes un assistant IA spécialisé dans la recherche d'informations sur les logiciels d'entreprise. Votre mission est de rechercher et compiler des informations détaillées sur chaque logiciel de la liste ci-dessous.

## INSTRUCTIONS
Pour chaque logiciel, recherchez sur internet et fournissez les informations suivantes :

### 1. DESCRIPTION DÉTAILLÉE
- Description complète du logiciel (minimum 200 mots)
- À quoi sert ce logiciel
- Public cible (PME, grandes entreprises, secteur spécifique)

### 2. FONCTIONNALITÉS PRINCIPALES
- Liste des 5-10 fonctionnalités clés
- Modules ou composants principaux
- Intégrations possibles avec d'autres outils

### 3. SPÉCIFICITÉS TECHNIQUES
- Type de déploiement (Cloud, On-premise, Hybride)
- Compatibilité (Windows, Mac, Linux, Mobile)
- Technologies utilisées si disponibles
- API disponibles

### 4. INFORMATIONS COMMERCIALES
- Modèle de tarification (gratuit, freemium, payant)
- Gamme de prix approximative
- Versions disponibles (Starter, Pro, Enterprise, etc.)

### 5. POINTS FORTS ET DIFFÉRENCIATEURS
- Avantages concurrentiels
- Ce qui distingue ce logiciel de ses concurrents
- Cas d'usage spécifiques

### 6. INFORMATIONS ÉDITEUR
- Nom de l'entreprise éditrice
- Année de création du logiciel
- Localisation du siège social
- Taille de l'entreprise si disponible

## FORMAT DE RÉPONSE
Pour chaque logiciel, structurez votre réponse ainsi :

```
## [NOM DU LOGICIEL]

**Description :**
[Description détaillée]

**Fonctionnalités principales :**
- Fonctionnalité 1
- Fonctionnalité 2
- [...]

**Spécificités techniques :**
- Déploiement : [Cloud/On-premise/Hybride]
- Compatibilité : [Plateformes supportées]
- Intégrations : [Principales intégrations]

**Informations commerciales :**
- Modèle : [Gratuit/Freemium/Payant]
- Prix : [Gamme de prix]
- Versions : [Différentes éditions]

**Points forts :**
- [Avantage 1]
- [Avantage 2]
- [...]

**Éditeur :**
- Entreprise : [Nom]
- Création : [Année]
- Localisation : [Pays/Ville]

---
```

## LISTE DES LOGICIELS À RECHERCHER

"""
        return prompt

    def _export_txt(self, software_list, ai_prompt, filename):
        with open(f'{filename}.txt', 'w', encoding='utf-8') as f:
            f.write(ai_prompt)
            
            for i, software in enumerate(software_list, 1):
                f.write(f"{i}. **{software['name']}**\n")
                if software['site']:
                    f.write(f"   - Site web : {software['site']}\n")
                if software['current_description']:
                    f.write(f"   - Description actuelle : {software['current_description'][:200]}...\n")
                if software['categories']:
                    f.write(f"   - Catégories : {', '.join(software['categories'])}\n")
                if software['metier']:
                    f.write(f"   - Métier : {software['metier']}\n")
                if software['company']:
                    f.write(f"   - Éditeur : {software['company']}\n")
                f.write("\n")
            
            f.write(f"\n\n## STATISTIQUES\n")
            f.write(f"- Total de logiciels à rechercher : {len(software_list)}\n")
            f.write(f"- Date d'export : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"- Logiciels avec site web : {sum(1 for s in software_list if s['site'])}\n")
            f.write(f"- Logiciels avec description : {sum(1 for s in software_list if s['current_description'])}\n")

    def _export_json(self, software_list, ai_prompt, filename):
        data = {
            'ai_prompt': ai_prompt,
            'software_list': software_list,
            'export_date': datetime.now().isoformat(),
            'total_count': len(software_list),
            'statistics': {
                'with_website': sum(1 for s in software_list if s['site']),
                'with_description': sum(1 for s in software_list if s['current_description']),
                'with_company': sum(1 for s in software_list if s['company']),
            }
        }
        
        with open(f'{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2) 