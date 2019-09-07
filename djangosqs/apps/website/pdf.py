from djangosqs import settings
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer

import hashlib
import typing as t


class Pdf:
    file_name: t.Optional[str] = None
    receipt_url: t.Optional[str] = None

    def __init__(self) -> None:
        font: str = "{}/fonts/{}".format(settings.STATIC_ROOT, "RobotoSlab-Regular.ttf")
        pdfmetrics.registerFont(TTFont("roboto", font))

    def receipt(self, message: t.Dict[str, str]) -> str:

        receipt = []

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="pizza-title",
                fontName="roboto",
                fontSize=16,
                leading=18,
                alignment=TA_CENTER,
            )
        )
        styles.add(
            ParagraphStyle(
                name="pizza-center",
                fontName="roboto",
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
            )
        )

        styles.add(
            ParagraphStyle(
                name="pizza-normal",
                fontName="roboto",
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY,
            )
        )

        text = "Receipt {}".format(message["receipt_id"])
        receipt.append(Paragraph(text, styles["pizza-title"]))
        receipt.append(Spacer(1, 25))

        text = "Thanks for using {}. This PDF is the receipt for your purchase. No payment is due.".format(
            message["product_name"]
        )
        receipt.append(Paragraph(text, styles["pizza-center"]))
        receipt.append(Spacer(1, 25))

        pizza_image = "{}/{}".format(settings.MEDIA_ROOT, message["image"])
        receipt.append(Image(pizza_image))
        receipt.append(Spacer(1, 25))

        hash_object = hashlib.md5(message["receipt_id"].encode())
        file_name = "receipt/{}.pdf".format(hash_object.hexdigest())

        doc = SimpleDocTemplate(
            "{}/{}".format(settings.MEDIA_ROOT, file_name),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=150,
            bottomMargin=0,
        )
        doc.build(receipt)

        self.file_name = file_name
        self.receipt_url = "http://127.0.0.1:8000/media/{}".format(file_name)

        return self.file_name
