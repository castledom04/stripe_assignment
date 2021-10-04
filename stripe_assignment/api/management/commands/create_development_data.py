from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Account, User


class Command(BaseCommand):
    help = 'Creates development data user and account'

    def handle(self, *args, **kwargs):
        if settings.ENVIRONMENT != 'production' and not User.objects.filter(username='admin').exists():
            print('Creating development data...')
            account = Account.objects.create(name="Admin account")
            self.user = User.objects.create_superuser(
                username='admin',
                password='qweqweqwE1',
                first_name='Admin',
                last_name='Super',
                account=account
            )
