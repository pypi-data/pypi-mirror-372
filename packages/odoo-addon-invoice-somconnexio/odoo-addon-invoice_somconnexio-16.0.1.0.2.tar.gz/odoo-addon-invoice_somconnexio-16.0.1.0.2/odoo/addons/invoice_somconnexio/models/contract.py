from odoo import models


class Contract(models.Model):
    _inherit = "contract.contract"

    def _get_related_invoices(self):
        self.ensure_one()
        invoices = super()._get_related_invoices()
        invoices += (
            self.env["contract.account.invoice.line.relation"]
            .search([("contract_id", "=", self.id)])
            .mapped("account_invoice_line_id")
            .mapped("move_id")
        )
        return invoices
