from django.core.management.base import BaseCommand
from sevy_app.models import SystemConfig

class Command(BaseCommand):
    help = 'Seeds the platform commission percentage (28%) into the SystemConfig table'

    def handle(self, *args, **kwargs):
        config, created = SystemConfig.objects.get_or_create(id=1)
        
        config.platform_commission_percentage = 28.00
        config.save()

        if created:
            self.stdout.write(self.style.SUCCESS('Created new SystemConfig and set commission to 28%.'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated existing SystemConfig and set commission to 28%.'))
