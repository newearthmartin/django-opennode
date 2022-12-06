# django-opennode
Django app for receiving payments with OpenNode

## Status:

I'm using this library to receive payments on my projects. It is not complete but does the job. Contributions are welcome.

## Usage:

### Settings:

```python
INSTALLED_APPS = [
    #...
    'opennode'
]
```

In your production settings file, define:
```python
OPENNODE_API_KEY = "YOUR_PRODUCTION_OPENNODE_API_KEY"
OPENNODE_ENDPOINT = 'https://api.opennode.com'
```

In your testing settings file, use:

```python
OPENNODE_API_KEY = "YOUR_TESTING_OPENNODE_API_KEY"
OPENNODE_ENDPOINT = 'https://dev-api.opennode.com'
```



### URLS:

Django-opennode provides a view for handling webhooks from OpenNode. 
Additionally, you can supply a success return URL and also you would need to have a view that creates a charge:


```python
from opennode.views import opennode_charge_webhooks
from your_project.views import opennode_success, opennode_create_charge

urlpatterns = [
    #...
    # view from django-opennode:
    path('opennode/charge/webhooks', opennode_charge_webhooks),
    
    # your views:
    path('opennode/success', opennode_success), 
    path('opennode/charge/create', opennode_create_charge, name='opennode_create_charge'),
]
```

### Creating a charge

To create a charge, you need to call the `opennode.api.create_charge` method. You need to unpack the result of `opennode.api.create_charge` into `charge` and `error`. If error is `None`, you can send the user to the `hosted_checkout_url`, which is hosted by OpenNode.

This is an example of a view that creates the charge and redirects to OpenNode's hosted checkout page:

```python
from opennode.api import create_charge
from opennode.views import opennode_charge_webhooks
from your_project.views import opennode_success

def opennode_create_charge(request):
    order_id = 'order-1234'
    description = 'My order description'
    buyer_email = 'client@email.com'
    price = 10
    currency = 'USD'
    
    webhooks_url = 'https://yourserver.domain' + reverse(opennode_charge_webhooks)
    success_url = 'https://yourserver.domain' + reverse(opennode_success)
    
    charge, error = create_charge(order_id, price, currency, webhooks_url, 
                                  description=description, notif_email=buyer_email,
                                  success_url=success_url)
    if error:
        return HttpResponseServerError(f'Error creating OpenNode charge: {error}')

    # adding ln=1 to prioritize Lightning Network
    return HttpResponseRedirect(charge.hosted_checkout_url + '?ln=1')  
```    


### Signal:

OpenNode will use the `opennode_charge_webhooks` URL to notify you of changes to charges. This view will trigger the signal `opennode.signals.opennode_charge_event_received` which you can subscribe to. 

There are many state changes and not all webhooks mean that a charge has been paid. You must check that the charge `status` is `"paid"`:

```python
from django.dispatch import receiver
from opennode.signals import opennode_charge_event_received

@receiver(opennode_charge_event_received)
def opennode_received(sender, **_):
    charge = sender.charge
    
    status = charge.status
    order_id = charge.order_id
    created_at = charge.created_at
    fiat_value = charge.source_fiat_value

    print(f'Opennode event received - {order_id} - {status}- {created_at} - {fiat_value}')
    
    if charge.status != 'paid':
        print(f'Charge {order_id} is not paid - ignoring')
        return
    
    print(f'Charge {order_id} is paid! - processing')    
    ...
```
