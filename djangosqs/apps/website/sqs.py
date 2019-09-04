from djangosqs.apps.website.pdf import Pdf
from djangosqs.apps.website.postmark import Postmark
from djangosqs.settings import DEFAULT_FROM_EMAIL

import boto3
import json
import time
import typing as t


class Sqs:
    def __init__(
        self,
        region_name: str,
        queue_name: str,
        dl_queue_name: str,
        template_id: str = "",
        delay_seconds: int = 0,
        visibility_timeout: int = 20,
        max_receive_count: int = 5,
        wait_seconds: int = 20,
        sleep_seconds: int = 5,
    ) -> None:
        self.delay_seconds = delay_seconds
        self.wait_seconds = wait_seconds
        self.sleep_seconds = sleep_seconds
        self.visibility_timeout = visibility_timeout
        self.template_id = template_id

        sqs = boto3.resource("sqs", region_name=region_name)

        dead_letter_queue_attributes = {"DelaySeconds": str(delay_seconds)}

        sqs.create_queue(
            QueueName=dl_queue_name, Attributes=dead_letter_queue_attributes
        )

        queue_dead_letter = sqs.get_queue_by_name(QueueName=dl_queue_name)
        queue_dead_letter_arn = queue_dead_letter.attributes["QueueArn"]

        redrive_policy = {
            "deadLetterTargetArn": queue_dead_letter_arn,
            "maxReceiveCount": str(max_receive_count),
        }
        standard_queue_attributes = {
            "DelaySeconds": str(delay_seconds),
            "ReceiveMessageWaitTimeSeconds": str(wait_seconds),
            "RedrivePolicy": json.dumps(redrive_policy),
        }

        self.queue = sqs.create_queue(
            QueueName=queue_name, Attributes=standard_queue_attributes
        )
        self.client = boto3.client("sqs", region_name=region_name)

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
