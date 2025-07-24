import json
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cabinet_digital.models import Software

class Command(BaseCommand):
    help = 'Import solutions from solutions.json file'

    def handle(self, *args, **options):
        # Path to the JSON file
        json_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'solutions.json')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                solutions = json.load(file)
            
            created_count = 0
            updated_count = 0
            
            for solution_data in solutions:
                name = solution_data.get('logiciel')
                slug = solution_data.get('slug')
                excerpt = solution_data.get('excerpt', '')
                description = solution_data.get('description', '')
                
                if not name or not slug:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping solution with missing name or slug: {solution_data}')
                    )
                    continue
                
                # Check if software already exists
                software, created = Software.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'excerpt': excerpt,
                        'description': description,
                        'is_published': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created software: {name}')
                    )
                else:
                    # Update existing software
                    software.name = name
                    software.excerpt = excerpt
                    software.description = description
                    software.is_published = True
                    software.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated software: {name}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed! Created: {created_count}, Updated: {updated_count}'
                )
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {json_file_path}')
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Error parsing JSON: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            ) 