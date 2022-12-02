from django.contrib import admin
from .models import OpennodeCharge, OpennodeChargeEvent

admin.site.register(OpennodeCharge, OpennodeCharge.Admin)
admin.site.register(OpennodeChargeEvent, OpennodeChargeEvent.Admin)
