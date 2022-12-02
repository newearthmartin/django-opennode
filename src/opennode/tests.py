from datetime import datetime
from django.test import TestCase
from .api import create_charge
from .views import process_webhooks
from .models import OpennodeChargeEvent


class OpennodeTest(TestCase):
    def test_charge(self):
        order_id = f'order_id_{int(datetime.now().timestamp() * 1000)}'
        charge, _ = create_charge(order_id, '12', 'USD', 'https://callback.url.doesnotexist.ok/')
        self.assertIsNotNone(charge)
        self.simulate_webhooks(charge.charge_id, 'processing')
        self.simulate_webhooks(charge.charge_id, 'paid')
        self.assertEqual(OpennodeChargeEvent.objects.filter(charge_id=charge.charge_id).count(), 2)

    @staticmethod
    def simulate_webhooks(charge_id, status):
        # FIXME: add more fields
        process_webhooks({
            'id': charge_id,
            'status': status
        })