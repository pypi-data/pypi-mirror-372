from pyopencell.resources.invoice import Invoice

from odoo import models

from ..backblaze.b2_service import B2Service


class DownloadInvoice(models.AbstractModel):
    _name = "download.invoice"
    _description = "Download Invoice Service"

    def download_invoice_pdf(self, invoice_number):
        # TODO review to change domain by single filter
        invoice = self.env["account.move"].search(
            ["|", ("name", "=", invoice_number), ("ref", "=", invoice_number)],
            limit=1,
        )
        if invoice.b2_file_id:
            invoice_base64 = B2Service().get_pdf_invoice(invoice.b2_file_id)
        else:
            invoice_base64 = Invoice.getInvoicePdfByNumber(invoice.ref)
        return invoice_base64
