from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Load sample CV data from fixtures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading fixtures',
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['clear']:
                self.stdout.write('Clearing existing data...')
                call_command('flush', '--noinput')
                self.stdout.write(
                    self.style.SUCCESS('Existing data cleared')
                )

            self.stdout.write('Loading initial CV data...')
            call_command('loaddata', 'initial_data.json')

            self.stdout.write('Loading additional CV data...')
            call_command('loaddata', 'initial_cv_data.json')

            self.stdout.write('Loading skills data...')
            call_command('loaddata', 'initial_skills_data.json')

            self.stdout.write('Loading projects data...')
            call_command('loaddata', 'initial_projects_data.json')

            self.stdout.write('Loading contacts data...')
            call_command('loaddata', 'initial_contacts_data.json')

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded all sample data!')
        )
