from odoo import models


class PaymentOrderConfirm(models.TransientModel):
    _name = "payment.order.confirm"
    _description = "Confirm Payment Orders"

    def run(self):
        payment_orders = self.env["account.payment.order"].browse(
            self._context["active_ids"]
        )
        return payment_orders.draft2open()
