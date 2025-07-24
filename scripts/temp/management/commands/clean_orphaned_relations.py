from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Nettoie les relations orphelines entre intégrateurs et logiciels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait supprimé sans effectuer la suppression',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== MODE DRY-RUN: Aucune suppression ne sera effectuée ==='))
        else:
            self.stdout.write(self.style.SUCCESS('=== Nettoyage des relations orphelines ==='))
        
        # Trouver les relations orphelines
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT is_rel.id, is_rel.integrator_id, is_rel.software_id, i.name as integrator_name
                FROM cabinet_digital_integrator_softwares is_rel
                LEFT JOIN cabinet_digital_integrator i ON is_rel.integrator_id = i.id
                LEFT JOIN cabinet_digital_software s ON is_rel.software_id = s.id
                WHERE s.id IS NULL
            """)
            
            orphaned_relations = cursor.fetchall()
            
            if not orphaned_relations:
                self.stdout.write(self.style.SUCCESS('✓ Aucune relation orpheline trouvée'))
                return
            
            self.stdout.write(f'🔍 {len(orphaned_relations)} relations orphelines trouvées:')
            
            integrator_counts = {}
            relation_ids_to_delete = []
            
            for relation_id, integrator_id, software_id, integrator_name in orphaned_relations:
                if integrator_name not in integrator_counts:
                    integrator_counts[integrator_name] = 0
                integrator_counts[integrator_name] += 1
                relation_ids_to_delete.append(relation_id)
                
                self.stdout.write(f'  - Relation ID {relation_id}: {integrator_name} -> Logiciel ID {software_id} (supprimé)')
            
            # Résumé par intégrateur
            self.stdout.write(f'\n📊 Résumé par intégrateur:')
            for integrator_name, count in integrator_counts.items():
                self.stdout.write(f'  - {integrator_name}: {count} relations orphelines')
            
            if not dry_run:
                # Confirmer avant suppression
                confirm = input(f'\n⚠️  Voulez-vous supprimer ces {len(relation_ids_to_delete)} relations orphelines ? (oui/non): ')
                
                if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                    with transaction.atomic():
                        # Supprimer les relations orphelines
                        cursor.execute("""
                            DELETE FROM cabinet_digital_integrator_softwares 
                            WHERE id IN ({})
                        """.format(','.join(['%s'] * len(relation_ids_to_delete))), relation_ids_to_delete)
                        
                        deleted_count = cursor.rowcount
                        
                    self.stdout.write(self.style.SUCCESS(f'✅ {deleted_count} relations orphelines supprimées'))
                    
                    # Vérification finale
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM cabinet_digital_integrator_softwares is_rel
                        LEFT JOIN cabinet_digital_software s ON is_rel.software_id = s.id
                        WHERE s.id IS NULL
                    """)
                    
                    remaining = cursor.fetchone()[0]
                    if remaining == 0:
                        self.stdout.write(self.style.SUCCESS('✅ Toutes les relations orphelines ont été nettoyées'))
                    else:
                        self.stdout.write(self.style.ERROR(f'⚠️  {remaining} relations orphelines restantes'))
                        
                else:
                    self.stdout.write(self.style.WARNING('❌ Suppression annulée'))
            else:
                self.stdout.write(f'\n💡 Pour effectuer le nettoyage, relancez sans --dry-run')
        
        self.stdout.write(self.style.SUCCESS('\n=== Nettoyage terminé ===')) 