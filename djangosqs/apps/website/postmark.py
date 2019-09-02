from django.core.mail import EmailMessage


class Postmark(EmailMessage):
    def __init__(
        self,
        subject: str = "",
        body="",
        from_email=None,
        to=None,
        bcc=None,
        connection=None,
        attachments=None,
        headers=None,
        cc=None,
        reply_to=None,
        template_id="",
        data={},
    ):
        self.template_id = template_id
        self.merge_global_data = data
        super(Postmark, self).__init__(
            subject,
            body,
            from_email,
            to,
            bcc,
            connection,
            attachments,
            headers,
            cc,
            reply_to,
        )
