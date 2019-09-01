from django.core.management.base import BaseCommand
from djangosqs.apps.website.sqs import Sqs


class Command(BaseCommand):

    help = "SQS Runner"

    def handle(self, *args, **options):

        print("========================")
        sqs = Sqs()

        while True:
            sqs.process_queue()

        print("========================")
        print("Done!")
