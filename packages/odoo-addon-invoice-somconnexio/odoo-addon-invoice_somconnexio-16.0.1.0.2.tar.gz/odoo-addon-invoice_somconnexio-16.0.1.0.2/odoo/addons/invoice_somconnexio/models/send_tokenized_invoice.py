import os
import urllib

from odoo import models

from odoo.addons.oficinavirtual_somconnexio.somoffice.user import SomOfficeUser


class SendTokenizedInvoice(models.AbstractModel):
    _name = "send.tokenized.invoice"
    _description = "Send Tokenized Invoice"

    def send_tokenized_invoice(self, record):
        token_response = SomOfficeUser(
            record.partner_id.ref,
            record.partner_id.email,
            record.partner_id.vat,
            record.partner_id.lang,
            self.env,
        ).generate_invoice_token(record.id)
        base_url = urllib.parse.urljoin(os.getenv("SOMOFFICE_URL"), "invoice")
        record.invoice_tokenized_url = f"{base_url}/{token_response['invoice_token']}?locale={record.partner_id.lang.split('_')[0]}"  # noqa
        record.company_id.customer_invoice_mail_template_id.send_mail(record.id, False)
