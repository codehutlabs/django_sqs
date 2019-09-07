from django.core.mail import EmailMessage
from email.mime.base import MIMEBase

import typing as t


class Postmark(EmailMessage):
    def __init__(
        self,
        from_email: str,
        to: t.List[str],
        template_id: str,
        subject: str = "",
        body: str = "",
        cc: t.Optional[t.List[str]] = None,
        bcc: t.Optional[t.List[str]] = None,
        reply_to: t.Optional[t.List[str]] = None,
        attachments: t.Optional[
            t.Sequence[t.Union[MIMEBase, t.Tuple[str, bytes, str]]]
        ] = None,
        headers: t.Optional[t.Dict[str, str]] = None,
        data: t.Dict[str, str] = {},
    ) -> None:
        self.template_id = template_id
        self.merge_global_data = data
        super(Postmark, self).__init__(
            subject, body, from_email, to, bcc, None, attachments, headers, cc, reply_to
        )
