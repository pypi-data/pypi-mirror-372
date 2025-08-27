from odoo.addons.component.core import Component

from bi_sc_client.services.notify_invoice_number import NotifyInvoiceNumber


class AccountInvoice(Component):
    _name = "account.invoice.listener"
    _inherit = "base.event.listener"
    _apply_on = ["account.move"]

    def on_record_write(self, record, fields=None):
        self._notify_invoice_number(record, fields)
        self._send_tokenized_invoice(record, fields)

    def _notify_invoice_number(self, record, fields):
        if (
            "state" in fields
            and record.state == "posted"
            and record.contract_group_id
            and record.journal_id
            == self.env.ref("invoice_somconnexio.customer_services_invoices_journal")
            and not record.b2_file_id
        ):
            NotifyInvoiceNumber(record.name).run()

    def _send_tokenized_invoice(self, record, fields):
        if "b2_file_id" in fields:
            self.env["send.tokenized.invoice"].with_delay().send_tokenized_invoice(
                record
            )
