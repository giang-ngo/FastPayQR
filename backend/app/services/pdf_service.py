import os
from jinja2 import Template
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)


def generate_invoice_pdf(order_id, user_name, amount):
    try:
        html_template = """
        <h2>Hóa đơn #{{ order_id }}</h2>
        <p>Tên: {{ user_name }}</p>
        <p>Số tiền: {{ amount }} VND</p>
        """
        html = Template(html_template).render(order_id=order_id, user_name=user_name, amount=amount)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        invoices_dir = os.path.join(BASE_DIR, "..", "..", "static", "invoices")
        os.makedirs(invoices_dir, exist_ok=True)

        tmp_file = os.path.join(invoices_dir, f"invoice_{order_id}.pdf")
        HTML(string=html).write_pdf(tmp_file)

        logger.info(f"PDF generated at {tmp_file}")
        return tmp_file
    except Exception as e:
        logger.exception(f"Error generating PDF: {e}")
        raise
