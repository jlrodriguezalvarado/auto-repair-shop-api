from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.catalog.models import ServiceCatalog
from apps.company.models import Company

User = get_user_model()

class Command(BaseCommand):
    help = "Seed multi-tenant demo data (superadmin + demo company + staff + catalog)"

    def handle(self, *args, **options):
        if not User.objects.filter(username="superadmin").exists():
            User.objects.create_user(
                username="superadmin",
                email="superadmin@example.com",
                password="superadmin123",
                role=User.Role.SUPER_ADMIN,
                company=None,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS("Super admin created: superadmin/superadmin123"))
        company, created = Company.objects.get_or_create(
            name="Taller Mecánico Demo",
            defaults={
                "tax_id": "J-00000000-0",
                "address": "Dirección del taller demo",
                "phone": "000-0000000",
                "email": "taller@example.com",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Demo company created: "Taller Mecánico Demo"'))
        staff = [
            ("admin", "admin@example.com", "admin123", User.Role.ADMINISTRATOR),
            ("secretary", "sec@example.com", "sec123", User.Role.SECRETARY),
            ("mechanic", "mech@example.com", "mech123", User.Role.MECHANIC),
        ]
        for username, email, password, role in staff:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    company=company,
                )
                self.stdout.write(self.style.SUCCESS(f"User created: {username}/{password} ({role})"))
            else:
                user = User.objects.get(username=username)
                if user.company_id != company.id:
                    user.company = company
                    user.role = role
                    user.save(update_fields=["company", "role"])
                    self.stdout.write(self.style.WARNING(f"User {username} reassigned to demo company"))
        services = [
            {"name": "Cambio de aceite", "base_price": 50.00, "estimated_duration_minutes": 30},
            {"name": "Alineación y Balanceo", "base_price": 80.00, "estimated_duration_minutes": 60},
            {"name": "Revisión de frenos", "base_price": 40.00, "estimated_duration_minutes": 45},
        ]
        for s in services:
            ServiceCatalog.objects.get_or_create(
                company=company,
                name=s["name"],
                defaults={
                    "base_price": s["base_price"],
                    "estimated_duration_minutes": s["estimated_duration_minutes"],
                },
            )
        self.stdout.write(self.style.SUCCESS("Demo catalog seeded for company"))
        self.stdout.write(self.style.SUCCESS("Seed completed"))
