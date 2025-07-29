# from backend.app.services.email_service import send_email_with_attachment
# from backend.app.utils.celery_worker import celery_app
# import logging
#
# logger = logging.getLogger(__name__)
#
# @celery_app.task(bind=True)
# def send_email_task(self, to_email, subject, body, attachment_path=None):
#     try:
#         logger.info(f"[EMAIL_TASK] Sending email to {to_email}")
#         send_email_with_attachment(to_email, subject, body, attachment_path)
#         logger.info(f"[EMAIL_TASK] Email sent to {to_email}")
#     except Exception as exc:
#         logger.error(f"[EMAIL_TASK] Failed: {exc}")
#         raise self.retry(exc=exc)
