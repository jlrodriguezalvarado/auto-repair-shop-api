from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.catalog.models import ServiceCatalog

User = get_user_model()

class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, *args, **options):
        # Create Admin
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123", role="ADMIN")
            self.stdout.write(self.style.SUCCESS("Admin user created: admin/admin123"))

        # Create Secretary
        if not User.objects.filter(username="secretary").exists():
            User.objects.create_user("secretary", "sec@example.com", "sec123", role="SECRETARY")
            self.stdout.write(self.style.SUCCESS("Secretary user created: secretary/sec123"))

        # Create Mechanic
        if not User.objects.filter(username="mechanic").exists():
            User.objects.create_user("mechanic", "mech@example.com", "mech123", role="MECHANIC")
            self.stdout.write(self.style.SUCCESS("Mechanic user created: mechanic/mech123"))

        # Create some services
        services = [
            {"name": "Cambio de aceite", "base_price": 50.00, "estimated_duration_minutes": 30},
            {"name": "Alineación y Balanceo", "base_price": 80.00, "estimated_duration_minutes": 60},
            {"name": "Revisión de frenos", "base_price": 40.00, "estimated_duration_minutes": 45},
        ]
        for s in services:
            ServiceCatalog.objects.get_or_create(name=s["name"], defaults=s)

        self.stdout.write(self.style.SUCCESS("Services seeded successfully"))
