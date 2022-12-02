import json
import hmac
import hashlib
import logging
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import OpennodeCharge, OpennodeChargeEvent
from .signals import opennode_charge_event_received

logger = logging.getLogger(__name__)


@csrf_exempt
def opennode_charge_webhooks(request):
    charge_id = request.POST['id']
    digest = hmac.new(settings.OPENNODE_API_KEY.encode(), charge_id.encode(), hashlib.sha256).hexdigest()
    if digest != request.POST['hashed_order']:
        logger.error(f'Invalid hashed_order for charge webhooks - id {charge_id}')
        return HttpResponseBadRequest()
    process_webhooks(request.POST)
    return HttpResponse()


def process_webhooks(data):
    charge_id = data['id']
    status = data['status']
    logger.info(f'OpenNode charge webhooks - {charge_id} - {status}')
    text_data = json.dumps(data)

    charge = OpennodeCharge.objects.filter(charge_id=charge_id).first()
    if not charge:
        logger.error(f'OpenNode charge not found for webhooks - id {charge_id}')
        return

    event = OpennodeChargeEvent(charge=charge, status=status, received_at=timezone.now(), data=text_data)
    event.save()

    if charge.status != status:
        charge.status = status
        charge.save()

    opennode_charge_event_received.send(event)
