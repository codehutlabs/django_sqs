from djangosqs.apps.website.pdf import Pdf
from djangosqs.apps.website.postmark import Postmark
from djangosqs.settings import DEFAULT_FROM_EMAIL
from djangosqs.settings import MICRO_CONFIG
from djangosqs.settings import TEMPLATE_ID

import boto3
import json
import time
import typing as t


class Sqs:
    def __init__(self):
        self.region_name = MICRO_CONFIG["REGION_NAME"]
        self.queue_name = MICRO_CONFIG["STANDARD_QUEUE"]
        self.dl_queue_name = MICRO_CONFIG["DL_QUEUE"]
        self.delay_seconds = MICRO_CONFIG["DELAY_SECONDS"]
        self.visibility_timeout = MICRO_CONFIG["VISIBILITY_TIMEOUT"]
        self.max_receive_count = MICRO_CONFIG["MAX_RECEIVE_COUNT"]
        self.wait_seconds = MICRO_CONFIG["WAIT_TIME_SECONDS"]
        self.sleep_seconds = MICRO_CONFIG["SLEEP_SECONDS"]

        self.template_id = TEMPLATE_ID

        sqs = boto3.resource("sqs", region_name=self.region_name)

        dead_letter_queue_attributes = {"DelaySeconds": str(self.delay_seconds)}

        sqs.create_queue(
            QueueName=self.dl_queue_name, Attributes=dead_letter_queue_attributes
        )

        queue_dead_letter = sqs.get_queue_by_name(QueueName=self.dl_queue_name)
        queue_dead_letter_arn = queue_dead_letter.attributes["QueueArn"]

        redrive_policy = {
            "deadLetterTargetArn": queue_dead_letter_arn,
            "maxReceiveCount": str(self.max_receive_count),
        }
        standard_queue_attributes = {
            "DelaySeconds": str(self.delay_seconds),
            "ReceiveMessageWaitTimeSeconds": str(self.wait_seconds),
            "RedrivePolicy": json.dumps(redrive_policy),
        }

        self.queue = sqs.create_queue(
            QueueName=self.queue_name, Attributes=standard_queue_attributes
        )
        self.client = boto3.client("sqs", region_name=self.region_name)

    def get_queue(self):
        return self.queue

    def send_message(
        self, message_body: t.Dict[str, t.Union[str, t.Dict[str, str]]]
    ) -> t.Dict[str, t.Union[str, t.Dict[str, t.Union[int, str, t.Dict[str, str]]]]]:

        body = json.dumps(message_body, sort_keys=True)

        response = self.client.send_message(
            QueueUrl=self.queue.url, MessageBody=body, DelaySeconds=self.delay_seconds
        )

        return response

    def process_queue(self):

        response = self.client.receive_message(
            QueueUrl=self.queue.url,
            AttributeNames=["SentTimestamp"],
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=self.visibility_timeout,
            WaitTimeSeconds=self.wait_seconds,
        )

        if response and "Messages" in response:
            response_message = response["Messages"][0]
            message_id = response_message["MessageId"]
            receipt_handle = response_message["ReceiptHandle"]

            message = json.loads(response_message["Body"])

            success = self.process_message(message)

            if success:
                print("Message {} processed.".format(message_id))
                self.client.delete_message(
                    QueueUrl=self.queue.url, ReceiptHandle=receipt_handle
                )
            else:
                print("There was an error with message {}.".format(message_id))

        time.sleep(self.sleep_seconds)

    def process_message(self, message: dict) -> bool:

        pdf = Pdf()

        message["action_url"] = pdf.receipt(message)

        postmark = Postmark(
            subject="",
            body="",
            from_email=DEFAULT_FROM_EMAIL,
            to=[message["to"]],
            template_id=self.template_id,
            data=message,
        )
        num_sent = postmark.send()

        return num_sent > 0
