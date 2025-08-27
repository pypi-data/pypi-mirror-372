from odoo import _, models


class PaymentReturnLine(models.Model):
    _inherit = "payment.return.line"

    def match_move_lines(self):
        for line in self:
            domain = line.partner_id and [("partner_id", "=", line.partner_id.id)] or []
            if line.return_id.journal_id:
                domain += [
                    ("journal_id", "=", line.return_id.journal_id.id),
                    ("move_id.move_type", "=", "entry"),
                ]
            domain.extend(
                [
                    ("account_id.account_type", "=", "asset_receivable"),
                    ("reconciled", "=", True),
                    "|",
                    ("name", "like", f"%{line.reference}%"),
                    ("ref", "like", f"%{line.reference}%"),
                ]
            )
            move_lines = self.env["account.move.line"].search(domain)
            if move_lines:
                line.move_line_ids = move_lines.ids
                if not line.concept:
                    line.concept = _("Move lines: %s") % ", ".join(
                        move_lines.mapped("name")
                    )
