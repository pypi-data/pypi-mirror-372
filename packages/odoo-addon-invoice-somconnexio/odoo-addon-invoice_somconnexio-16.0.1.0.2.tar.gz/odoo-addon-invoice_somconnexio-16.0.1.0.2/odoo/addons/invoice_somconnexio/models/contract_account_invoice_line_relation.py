from odoo import models, fields


class ContractAccountInvoiceLineRelation(models.Model):
    _name = "contract.account.invoice.line.relation"
    _description = "Relation between contract and account invoice line"

    account_invoice_line_id = fields.Many2one(
        "account.move.line", string="Invoice Line", required=True
    )
    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
