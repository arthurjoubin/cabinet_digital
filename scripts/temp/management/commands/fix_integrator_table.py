from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes the cabinet_digital_integrator_softwares table by adding software_id column'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Disable foreign key constraints temporarily
            cursor.execute("PRAGMA foreign_keys=OFF;")
            
            # Check if the column already exists to avoid errors
            cursor.execute("PRAGMA table_info(cabinet_digital_integrator_softwares)")
            columns = [column[1] for column in cursor.fetchall()]
            
            self.stdout.write(self.style.SUCCESS('Current columns:'))
            self.stdout.write(f"  {columns}")
            
            if 'software_id' not in columns:
                # Try to rename integratorsoftware_id to software_id if it exists
                if 'integratorsoftware_id' in columns:
                    self.stdout.write(self.style.WARNING('Attempting to rename integratorsoftware_id to software_id...'))
                    
                    try:
                        # First, let's inspect the content of the table
                        cursor.execute("SELECT * FROM cabinet_digital_integrator_softwares LIMIT 5;")
                        sample_data = cursor.fetchall()
                        self.stdout.write(self.style.SUCCESS('Sample data from existing table:'))
                        for row in sample_data:
                            self.stdout.write(f"  {row}")
                        
                        # Drop the temporary table if it exists
                        cursor.execute("DROP TABLE IF EXISTS cabinet_digital_integrator_softwares_new;")
                            
                        # Create a temporary table with the correct structure
                        cursor.execute("""
                        CREATE TABLE cabinet_digital_integrator_softwares_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            integrator_id INTEGER NOT NULL,
                            software_id INTEGER NOT NULL
                        );
                        """)
                        
                        # Copy data with renamed column
                        cursor.execute("""
                        INSERT INTO cabinet_digital_integrator_softwares_new (id, integrator_id, software_id)
                        SELECT id, integrator_id, integratorsoftware_id FROM cabinet_digital_integrator_softwares;
                        """)
                        
                        # Verify data was copied correctly
                        cursor.execute("SELECT COUNT(*) FROM cabinet_digital_integrator_softwares;")
                        old_count = cursor.fetchone()[0]
                        cursor.execute("SELECT COUNT(*) FROM cabinet_digital_integrator_softwares_new;")
                        new_count = cursor.fetchone()[0]
                        
                        if old_count != new_count:
                            self.stdout.write(self.style.WARNING(f'Data count mismatch: {old_count} in original table, {new_count} in new table'))
                            return
                        
                        # Drop old table
                        cursor.execute("DROP TABLE cabinet_digital_integrator_softwares;")
                        
                        # Rename new table to old name
                        cursor.execute("ALTER TABLE cabinet_digital_integrator_softwares_new RENAME TO cabinet_digital_integrator_softwares;")
                        
                        # Add the unique constraint back
                        cursor.execute("""
                        CREATE UNIQUE INDEX IF NOT EXISTS cabinet_digital_integrator_softwares_integrator_id_software_id_idx
                        ON cabinet_digital_integrator_softwares (integrator_id, software_id);
                        """)
                        
                        # Check the new structure
                        cursor.execute("SELECT * FROM cabinet_digital_integrator_softwares LIMIT 5;")
                        new_sample_data = cursor.fetchall()
                        self.stdout.write(self.style.SUCCESS('Sample data from new table:'))
                        for row in new_sample_data:
                            self.stdout.write(f"  {row}")
                        
                        self.stdout.write(self.style.SUCCESS('Successfully renamed integratorsoftware_id to software_id'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error renaming column: {e}'))
                        return
                else:
                    self.stdout.write(self.style.ERROR('integratorsoftware_id column not found. Migration can\'t proceed.'))
                    return
            else:
                self.stdout.write(self.style.SUCCESS('software_id column already exists. No action needed.'))

            # Re-enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON;")
            
            # Validate the table structure
            cursor.execute("PRAGMA table_info(cabinet_digital_integrator_softwares)")
            self.stdout.write(self.style.SUCCESS('Current table structure:'))
            for column in cursor.fetchall():
                self.stdout.write(f"  {column}") 