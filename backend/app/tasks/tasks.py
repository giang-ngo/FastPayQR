import logging
from backend.app.utils.celery_worker import celery_app
from backend.app.services.pdf_service import generate_invoice_pdf
from backend.app.services.email_service import send_email_with_attachment

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def send_email_task(self, to_email, subject, body, attachment_path=None):
    try:
        logger.info(f"[EMAIL_TASK] Sending email to {to_email}")
        send_email_with_attachment(to_email, subject, body, attachment_path)
        logger.info(f"[EMAIL_TASK] Email sent to {to_email}")
    except Exception as exc:
        logger.error(f"[EMAIL_TASK] Failed: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True)
def send_invoice_email_task(self, order_id, user_email, user_name, amount):
    try:
        logger.info(f"📄 Bắt đầu tạo PDF cho order {order_id}")
        pdf_path = generate_invoice_pdf(order_id, user_name, amount)

        logger.info(f"PDF tạo xong: {pdf_path}")

        logger.info(f"Đang gửi mail đến: {user_email}")
        send_email_with_attachment(
            to_email=user_email,
            subject="Invoice for your order",
            body=f"Dear {user_name},\n\nThank you for your payment. Please find attached your invoice.",
            attachment_path=pdf_path,
        )
        logger.info("Gửi mail thành công")
    except Exception as exc:
        logger.exception(f"Task lỗi: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
