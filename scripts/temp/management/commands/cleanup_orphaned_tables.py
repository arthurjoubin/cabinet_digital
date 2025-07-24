from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Clean up orphaned integrator tables'

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up orphaned integrator tables...")
        
        with connection.cursor() as cursor:
            # List of orphaned tables to clean up
            orphaned_tables = [
                'cabinet_digital_integrator_category',
                'cabinet_digital_integratorcategory'
            ]
            
            for table in orphaned_tables:
                try:
                    # Check if table exists
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if cursor.fetchone():
                        # Get count before deletion
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        
                        # Drop the table
                        cursor.execute(f"DROP TABLE IF EXISTS {table}")
                        self.stdout.write(f"Dropped table {table} (had {count} records)")
                    else:
                        self.stdout.write(f"Table {table} does not exist")
                        
                except Exception as e:
                    self.stdout.write(f"Error handling {table}: {e}")
            
            # Verify cleanup
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%integrator%category%'
            """)
            remaining = cursor.fetchall()
            
            if remaining:
                self.stdout.write(f"Warning: Some tables still exist: {[r[0] for r in remaining]}")
            else:
                self.stdout.write("✓ All orphaned integrator category tables cleaned up")
        
        self.stdout.write("Cleanup completed!") 