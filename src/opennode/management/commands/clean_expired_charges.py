from django.core.management.base import BaseCommand
from opennode.models import OpennodeCharge


class Command(BaseCommand):
    help = 'Removes expired OpenNode charges'

    def handle(self, *args, **options):
        charges = OpennodeCharge.objects.filter(status='expired')
        if charges.count() == 0:
            print('There are no expired charges.')
            return

        print(f'Deleting {charges.count()} expired charges')
        for charge in charges.all():
            charge.delete()
