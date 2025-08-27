from odoo import fields, models, _
import base64
import csv


class ContractInvoicePayment(models.TransientModel):
    _name = "contract.invoice.payment.wizard"
    _description = "Contract Invoice Payment"

    data = fields.Binary("Upload file")
    errors = fields.Text("Errors")
    state = fields.Selection(
        [
            ("errors", "errors"),
            ("load", "load"),
        ],
        default="load",
    )

    def run_wizard(self):
        decoded_data = base64.b64decode(self.data)
        f = (line.strip() for line in decoded_data.decode("utf-8").split("\n"))
        fr = csv.DictReader(f)
        errors = []
        for row in fr:
            invoice = self.env["account.move"].search(
                [("name", "=", row["Invoice number"])]
            )
            if not invoice:
                errors.append(
                    _(
                        f"The invoice {row['Invoice number']} has not be found (the contract is {row['Subscription code']})"  # noqa
                    )
                )
                continue
            contract = self.env["contract.contract"].search(
                [("code", "=", row["Subscription code"])]
            )
            if not contract:
                errors.append(
                    _(
                        f"The contract {row['Subscription code']} has not be found (the invoice is {row['Invoice number']})"  # noqa
                    )
                )
                continue
            contract = contract[0]
            invoice.payment_mode_id = contract.payment_mode_id
            invoice.mandate_id = contract.mandate_id
        if errors:
            self.errors = "\n".join(errors)
            self.state = "errors"
            return {
                "type": "ir.actions.act_window",
                "res_model": "contract.invoice.payment.wizard",
                "view_mode": "form",
                "res_id": self.id,
                "views": [(False, "form")],
                "target": "new",
            }
        return True
