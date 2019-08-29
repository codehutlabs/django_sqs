from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from djangosqs import settings

import hashlib


class Pdf:
    receipt_url = None

    def __init__(self):
        font = "{}/fonts/{}".format(settings.STATIC_ROOT, "RobotoSlab-Regular.ttf")
        pdfmetrics.registerFont(TTFont("roboto", font))

    def receipt(self, message):

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

        self.receipt_url = "http://127.0.0.1:8000/media/{}".format(file_name)

        return self.receipt_url
