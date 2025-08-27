from odoo import api, fields, models

from odoo.addons.queue_job.job import identity_exact


class AccountInvoiceConfirmBetweenDates(models.TransientModel):
    _name = "account.invoice.confirm.between.dates"
    _description = "Confirm Invoices Between Dates"

    @api.model
    def _default_journal(self):
        return self.env.ref("invoice_somconnexio.customer_services_invoices_journal")

    journal_id = fields.Many2one(
        "account.journal", string="Journal", required=True, default=_default_journal
    )

    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")

    def run_wizard(self):
        # Select all invoices between start and end date in draft state
        invoices = self.env["account.move"].search(
            [
                ("state", "=", "draft"),
                ("invoice_date", ">=", self.start_date),
                ("invoice_date", "<=", self.end_date),
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("release_capital_request", "=", False),
                ("journal_id", "=", self.journal_id.id),
            ]
        )
        # Confirm invoices with the account_invoice_confirm wizard
        for invoice in invoices:
            invoice.with_delay(
                priority=30,
                identity_key=identity_exact,
            ).action_post_job()
