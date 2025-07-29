from celery import Celery

celery_app = Celery(
    "fastpayqr",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["backend.app.tasks.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
)
