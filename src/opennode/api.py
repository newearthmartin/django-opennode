import json
import logging
import requests
from datetime import datetime
from django.conf import settings
from django.utils.timezone import make_aware
from .models import OpennodeCharge

logger = logging.getLogger(__name__)


def create_charge(order_id, amount, currency, callback_url, description=None, customer_email=None, customer_name=None, notif_email=None, success_url=None, ttl=10):
    data = {
        "order_id": order_id,
        "amount": amount,
        "description": description,
        "currency": currency,
        "callback_url": callback_url,
        "auto_settle": False,
        "ttl": ttl,
    }
    if description: data['description'] = description
    if customer_email: data['customer_email'] = customer_email
    if notif_email: data['notif_email'] = notif_email
    if customer_name: data['customer_name'] = customer_name
    if success_url: data['success_url'] = success_url

    headers = {'Authorization': settings.OPENNODE_API_KEY}

    logger.info(f'Creating OpenNode charge for {order_id}')
    response = requests.post(f'{settings.OPENNODE_ENDPOINT }/v1/charges', json=data, headers=headers)
    data = response.json()
    if response.status_code != 200:
        return None, data.get('message', f'error {response.status_code}')

    data = data['data']
    charge = OpennodeCharge(
        charge_id=data['id'],
        order_id=data['order_id'],
        description=data['description'] if data['description'] != 'N/A' else None,
        created_at=make_aware(datetime.fromtimestamp(data['created_at'])),
        status=data['status'],
        amount=data['amount'],
        currency=data['currency'],
        source_fiat_value=data['source_fiat_value'],
        auto_settle=data['auto_settle'],
        callback_url=data['callback_url'],
        success_url=data['success_url'],
        hosted_checkout_url=data['hosted_checkout_url'],
        notif_email=data['notif_email'],
        address=data['address'],
        metadata=json.dumps(data['metadata']) if data['metadata'] else None,
        chain_invoice=json.dumps(data['chain_invoice']) if data['chain_invoice'] else None,
        lightning_invoice=json.dumps(data['lightning_invoice']) if data['lightning_invoice'] else None,
        uri=data['uri'],
        ttl=data['ttl'],
    )
    charge.save()
    return charge, None
