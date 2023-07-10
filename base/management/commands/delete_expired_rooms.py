from django.core.management.base import BaseCommand
from django.db.models.functions import Now

from ...models import Room

class Command(BaseCommand):
    help = 'Remove expired stories'

    def handle(self, *args, **options):
        Room._base_manager.filter(expiration_time__gte=Now()).delete()