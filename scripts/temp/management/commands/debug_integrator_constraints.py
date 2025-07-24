from django.core.management.base import BaseCommand
from django.db import connection
from cabinet_digital.models import Integrator

class Command(BaseCommand):
    help = 'Debug integrator foreign key constraints'

    def handle(self, *args, **options):
        self.stdout.write("Debugging integrator constraints...")
        
        with connection.cursor() as cursor:
            # Check all tables that reference integrator
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND sql LIKE '%integrator%'
            """)
            tables = cursor.fetchall()
            
            self.stdout.write(f"Tables mentioning 'integrator': {[t[0] for t in tables]}")
            
            # Check foreign key constraints
            cursor.execute("PRAGMA foreign_key_list(cabinet_digital_integrator)")
            fk_constraints = cursor.fetchall()
            self.stdout.write(f"Foreign keys FROM integrator table: {fk_constraints}")
            
            # Check what references integrator table
            for table_name, in tables:
                if 'integrator' in table_name.lower():
                    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                    constraints = cursor.fetchall()
                    if constraints:
                        self.stdout.write(f"Foreign keys in {table_name}: {constraints}")
            
            # Check specific problematic tables
            problematic_tables = [
                'cabinet_digital_integrator_softwares',
                'cabinet_digital_platformedematerialisation_integrators',
                'cabinet_digital_integratorreview',
                'cabinet_digital_integratorreviewimage'
            ]
            
            for table in problematic_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f"Records in {table}: {count}")
                    
                    if 'integrator' in table and count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                        sample = cursor.fetchall()
                        self.stdout.write(f"Sample from {table}: {sample}")
                except Exception as e:
                    self.stdout.write(f"Error checking {table}: {e}")
        
        # Test individual integrator deletion
        integrators = Integrator.objects.all()[:3]
        for integrator in integrators:
            self.stdout.write(f"\nTesting {integrator.name} (ID: {integrator.id}):")
            
            # Check direct relationships
            software_count = integrator.softwares.count()
            review_count = integrator.reviews.count()
            pdp_count = integrator.pdp_platforms.count()
            
            self.stdout.write(f"  - Software relations: {software_count}")
            self.stdout.write(f"  - Reviews: {review_count}")
            self.stdout.write(f"  - PDP relations: {pdp_count}")
            
            # Try to clear and delete
            try:
                integrator.softwares.clear()
                integrator.pdp_platforms.clear()
                # Don't actually delete, just test
                self.stdout.write(f"  - Relations cleared successfully")
            except Exception as e:
                self.stdout.write(f"  - Error clearing relations: {e}") 