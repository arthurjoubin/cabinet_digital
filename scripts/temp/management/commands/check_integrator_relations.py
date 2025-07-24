from django.core.management.base import BaseCommand
from cabinet_digital.models import Integrator, PlatformeDematerialisation, IntegratorReview

class Command(BaseCommand):
    help = 'Check integrator foreign key relationships'

    def handle(self, *args, **options):
        self.stdout.write("Checking integrator relationships...")
        
        # Check PDP relationships
        pdps_with_integrators = PlatformeDematerialisation.objects.filter(integrators__isnull=False).distinct()
        self.stdout.write(f"PDPs with integrators: {pdps_with_integrators.count()}")
        
        for pdp in pdps_with_integrators:
            integrator_count = pdp.integrators.count()
            self.stdout.write(f"  - {pdp.name}: {integrator_count} integrators")
            for integrator in pdp.integrators.all():
                self.stdout.write(f"    * {integrator.name} (ID: {integrator.id})")
        
        # Check review relationships
        integrators_with_reviews = Integrator.objects.filter(reviews__isnull=False).distinct()
        self.stdout.write(f"\nIntegrators with reviews: {integrators_with_reviews.count()}")
        
        for integrator in integrators_with_reviews:
            review_count = integrator.reviews.count()
            self.stdout.write(f"  - {integrator.name}: {review_count} reviews")
        
        # Check software relationships
        integrators_with_software = Integrator.objects.filter(softwares__isnull=False).distinct()
        self.stdout.write(f"\nIntegrators with software: {integrators_with_software.count()}")
        
        for integrator in integrators_with_software:
            software_count = integrator.softwares.count()
            self.stdout.write(f"  - {integrator.name}: {software_count} software") 