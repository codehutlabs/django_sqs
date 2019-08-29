from django.core.mail import EmailMessage
from smtplib import SMTPException
from anymail.exceptions import AnymailError

from djangosqs.settings import MICRO_CONFIG, DEFAULT_FROM_EMAIL, TEMPLATE_ID
from djangosqs.apps.website.pdf import Pdf

import boto3
import json
import time


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

    def send_message(self, message_body):

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

    def process_message(self, message):

        pdf = Pdf()

        valid = "gov.si" not in message["to"]
        success = False

        if valid:
            message["action_url"] = pdf.receipt(message)
            success = self.send_notification(message)

        return success

    def send_notification(self, message):

        success = False

        to = message["to"]
        notification_mail = EmailMessage(
            to=[to], from_email=DEFAULT_FROM_EMAIL, subject=None, body=None
        )
        notification_mail.template_id = self.template_id
        notification_mail.merge_global_data = message

        try:
            notification_mail.send()
            success = True
        except AnymailError as e:
            print("AnymailError: There was an error sending an email.", e)
        except SMTPException as e:
            print("SMTPException: There was an error sending an email.", e)

        return success
