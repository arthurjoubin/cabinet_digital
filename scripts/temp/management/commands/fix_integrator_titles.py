from django.core.management.base import BaseCommand
from cabinet_digital.models import Integrator
import re


class Command(BaseCommand):
    help = 'Modifie en masse les descriptions des intégrateurs pour enlever les majuscules des titres sauf le premier mot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les modifications sans les appliquer',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY RUN - Aucune modification ne sera appliquée'))
        
        integrators = Integrator.objects.all()
        modified_count = 0
        
        for integrator in integrators:
            original_description = integrator.description
            modified_description = self.fix_titles_capitalization(original_description)
            
            if original_description != modified_description:
                modified_count += 1
                
                if dry_run:
                    self.stdout.write(f'\n--- {integrator.name} ---')
                    self.stdout.write('AVANT:')
                    self.stdout.write(original_description[:500] + '...' if len(original_description) > 500 else original_description)
                    self.stdout.write('\nAPRÈS:')
                    self.stdout.write(modified_description[:500] + '...' if len(modified_description) > 500 else modified_description)
                    self.stdout.write('-' * 50)
                else:
                    integrator.description = modified_description
                    integrator.save()
                    self.stdout.write(f'✅ Modifié: {integrator.name}')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nNombre d\'intégrateurs qui seraient modifiés: {modified_count}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nNombre d\'intégrateurs modifiés: {modified_count}'))

    def fix_titles_capitalization(self, description):
        """
        Modifie la capitalisation des titres dans la description HTML.
        Garde seulement la première lettre du premier mot en majuscule.
        """
        if not description:
            return description
        
        # Patterns pour identifier les titres dans les balises <strong> et les listes
        patterns = [
            # Titres dans <strong>
            (r'<strong>([^<]+):</strong>', self.fix_title_case),
            # Titres dans <li><strong>
            (r'<li><strong>([^<]+):</strong>', self.fix_title_case_in_li),
        ]
        
        modified_description = description
        
        for pattern, replacement_func in patterns:
            modified_description = re.sub(pattern, replacement_func, modified_description)
        
        return modified_description

    def fix_title_case(self, match):
        """Fonction de remplacement pour les titres dans <strong>"""
        title = match.group(1)
        fixed_title = self.capitalize_first_word_only(title)
        return f'<strong>{fixed_title}:</strong>'

    def fix_title_case_in_li(self, match):
        """Fonction de remplacement pour les titres dans <li><strong>"""
        title = match.group(1)
        fixed_title = self.capitalize_first_word_only(title)
        return f'<li><strong>{fixed_title}:</strong>'

    def capitalize_first_word_only(self, text):
        """
        Met en majuscule seulement la première lettre du premier mot.
        Garde les acronymes et mots spéciaux intacts.
        """
        if not text:
            return text
        
        # Mots qui doivent rester en majuscules (acronymes, etc.)
        preserve_uppercase = [
            'ERP', 'CRM', 'BI', 'RH', 'SIRH', 'PME', 'ETI', 'TPE', 'PMI',
            'AI', 'IA', 'API', 'SaaS', 'P2P', 'O2C', 'TMA', 'GED', 'GPEC',
            'GTA', 'DAF', 'CEO', 'CFO', 'CTO', 'DRH', 'DSI', 'IT', 'HR',
            'B2B', 'B2C', 'ROI', 'KPI', 'SQL', 'XML', 'JSON', 'REST',
            'GDPR', 'RGPD', 'ISO', 'QUALIOPI', 'TVA', 'HT', 'TTC'
        ]
        
        # Diviser en mots
        words = text.split()
        if not words:
            return text
        
        result_words = []
        
        for i, word in enumerate(words):
            # Nettoyer le mot des caractères spéciaux pour la vérification
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word.upper() in preserve_uppercase:
                # Garder les acronymes en majuscules
                result_words.append(word)
            elif i == 0:
                # Premier mot: première lettre en majuscule, le reste en minuscule
                if word:
                    result_words.append(word[0].upper() + word[1:].lower())
                else:
                    result_words.append(word)
            else:
                # Autres mots: tout en minuscule
                result_words.append(word.lower())
        
        return ' '.join(result_words) 