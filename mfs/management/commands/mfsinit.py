from django.core.management.base import BaseCommand
from mfs.init import create_initial_permissions


class Command(BaseCommand):
    """Command line of the database initialization. """

    def handle(self, *args, **kwargs):
        """ Function of module initialization. """
        create_initial_permissions()

