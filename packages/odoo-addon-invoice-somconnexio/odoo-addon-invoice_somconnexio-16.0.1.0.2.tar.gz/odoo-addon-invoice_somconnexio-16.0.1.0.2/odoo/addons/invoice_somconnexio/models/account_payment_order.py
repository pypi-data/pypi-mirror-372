from odoo import models, fields


class AccountPaymentOrder(models.Model):
    _inherit = "account.payment.order"

    set_uploaded_job_ids = fields.Many2many(
        comodel_name="queue.job",
        column1="account_payment_order_id",
        column2="job_id",
        string="Set as Uploaded Jobs",
        copy=False,
    )

    def generated2uploaded_job(self):
        self.ensure_one()
        if self.state != "generated":
            return
        self.generated2uploaded()

    def _prepare_move_line_offsetting_account(
        self, amount_company_currency, amount_payment_currency, bank_lines
    ):
        vals = super()._prepare_move_line_offsetting_account(
            amount_company_currency, amount_payment_currency, bank_lines
        )
        if vals.get("account_id") == self.payment_mode_id.transfer_account_id.id:
            vals["partner_id"] = False
        return vals

    def draft2open(self):
        super().draft2open()
        for order in self:
            for payline in order.payment_line_ids:
                if payline.move_line_id.move_id.journal_id == (
                    self.env.ref(
                        "invoice_somconnexio.customer_services_invoices_journal"
                    )
                ):
                    payline.purpose = "PHON"
