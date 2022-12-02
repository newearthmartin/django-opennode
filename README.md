# django-opennode
Django app for receiving payments with OpenNode

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

To create a charge call the `opennode.api.create_charge` method. You need to unpack the result into `charge` and `error`. 
If there is no error, you can redirect to OpenNode's hosted checkout URL.

You need to hook `opennode_charge_webhooks` from `django-opennode` into the webhooks_url and optionally provide a `success_url`.

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

Subscribe to `opennode.signals.opennode_charge_event_received` to be notified of opennode charges. 

```python
from django.dispatch import receiver
from opennode.signals import opennode_charge_event_received

@receiver(opennode_charge_event_received)
def opennode_received(sender, **_):
    charge = sender.charge

    if charge.status != 'paid':
        print(f'ignoring')
        return
        
    order_id = charge.order_id
    created_at = charge.created_at
    fiat_value = charge.source_fiat_value
    
    print(f'Opennode charge paid! - {order_id} - {created_at} - {fiat_value}')
```
