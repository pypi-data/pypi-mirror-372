from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from ... import settings


class Command(BaseCommand):
    help = 'Translate permission name'

    def handle(self, *args, **options):
        try:
            print('Start translating...')
            for permission in Permission.objects.all():
                action = settings.ACTIONS.get(permission.codename.split('_')[0])

                if action:
                    permission.name = '{0}{1}'.format(action, permission.content_type.name)
                    permission.save()
                    self.stdout.write(self.style.SUCCESS('Successfully translated app: "{}" - model: "{}"'.format(
                        permission.content_type.app_label,
                        permission.content_type.name)))
        except Exception as e:
            raise CommandError(str(e))
