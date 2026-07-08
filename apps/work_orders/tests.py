from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
from apps.work_orders.models import WorkOrder

User = get_user_model()

class WorkOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username="admin", password="password", role="ADMIN")
        self.client.force_authenticate(user=self.admin)
        self.customer = CustomerProfile.objects.create(first_name="Juan", last_name="Perez", phone="555-0001")
        self.vehicle = Vehicle.objects.create(customer=self.customer, plate="ABC-123")
        self.service = ServiceCatalog.objects.create(name="Aceite", base_price="50.00")

        self.order_data = {
            "customer": self.customer.id,
            "vehicle": self.vehicle.id,
            "status": "received"
        }

    def test_create_work_order(self):
        response = self.client.post("/api/work-orders/orders/", self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkOrder.objects.count(), 1)
        self.assertIsNotNone(WorkOrder.objects.get().code)

    def test_add_service_to_order(self):
        order = WorkOrder.objects.create(customer=self.customer, vehicle=self.vehicle)
        service_data = {
            "work_order": order.id,
            "service": self.service.id,
            "quantity": 1,
            "unit_price": "50.00"
        }
        response = self.client.post("/api/work-orders/order-services/", service_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.services.count(), 1)
        self.assertEqual(order.services.first().name_snapshot, "Aceite")

    def test_mechanic_visibility(self):
        mechanic = User.objects.create_user(username="mechanic", password="password", role="MECHANIC")
        order = WorkOrder.objects.create(customer=self.customer, vehicle=self.vehicle, assigned_mechanic=mechanic)
        order2 = WorkOrder.objects.create(customer=self.customer, vehicle=self.vehicle)

        self.client.force_authenticate(user=mechanic)
        response = self.client.get("/api/work-orders/orders/")
        self.assertEqual(len(response.data["results"]), 1)
