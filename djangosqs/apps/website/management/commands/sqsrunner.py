from django.core.management.base import BaseCommand
from djangosqs.apps.website.sqs import Sqs
from djangosqs.settings import MICRO_CONFIG


class Command(BaseCommand):

    help = "SQS Runner"

    def handle(self, *args, **options):

        print("========================")
        region_name = str(MICRO_CONFIG["REGION_NAME"])
        queue_name = str(MICRO_CONFIG["STANDARD_QUEUE"])
        dl_queue_name = str(MICRO_CONFIG["DL_QUEUE"])

        sqs = Sqs(
            region_name=region_name, queue_name=queue_name, dl_queue_name=dl_queue_name
        )

        while True:
            sqs.process_queue()

        print("========================")
        print("Done!")
