from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    customer_invoice_mail_template_id = fields.Many2one(
        "mail.template",
        string="Customer Invoice Mail Template",
        domain=[("model", "=", "account.move")],
        help="Used to send the invoice token to the customer",
    )
