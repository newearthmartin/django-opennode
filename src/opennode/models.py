from django.db import models
from django.contrib.admin import ModelAdmin


class OpennodeCharge(models.Model):
    charge_id = models.CharField(max_length=64)
    order_id = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField()
    status = models.CharField(max_length=16)
    amount = models.IntegerField()
    currency = models.CharField(max_length=3, null=True, blank=True)
    source_fiat_value = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    auto_settle = models.BooleanField()
    callback_url = models.CharField(max_length=256, null=True, blank=True)
    success_url = models.CharField(max_length=256, null=True, blank=True)
    hosted_checkout_url = models.CharField(max_length=256, null=True, blank=True)
    notif_email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    chain_invoice = models.TextField(null=True, blank=True)
    uri = models.CharField(max_length=512, null=True, blank=True)
    ttl = models.IntegerField(null=True, blank=True)
    lightning_invoice = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'opennode_charge_{self.pk}'

    class Admin(ModelAdmin):
        list_display = ['pk', 'charge_id', 'order_id', 'created_at', 'status']
        list_filter = ['status', 'currency']
        search_fields = ['charge_id', 'order_id', 'notif_email', 'address']


class OpennodeChargeEvent(models.Model):
    received_at = models.DateTimeField()
    charge = models.ForeignKey(OpennodeCharge, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=16)
    data = models.TextField()

    def __str__(self):
        return f'opennode_charge_event_{self.pk}'

    class Admin(ModelAdmin):
        list_display = ['pk', 'charge_id', 'status', 'received_at']
        list_filter = ['status']
        search_fields = ['charge__charge_id', 'charge__order_id', 'charge__notif_email', 'charge__address']
