import unittest
from odoo.tests.common import TransactionCase


class TestPaymentOrderInbound(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.inbound_mode = self.env.ref(
            "account_payment_mode.payment_mode_inbound_dd1"
        )
        self.journal = self.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                "|",
                ("company_id", "=", self.env.user.company_id.id),
                ("company_id", "=", False),
            ],
            limit=1,
        )
        if not self.journal:
            raise unittest.SkipTest("No journal found")
        self.inbound_mode.variable_journal_ids = self.journal
        # Make sure no others orders are present
        self.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "inbound"),
        ]
        self.payment_order_obj = self.env["account.payment.order"]
        self.payment_order_obj.search(self.domain).unlink()
        # Create payment order
        self.inbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_mode_id": self.inbound_mode.id,
                "journal_id": self.journal.id,
            }
        )
        self.account_id = self.ref("l10n_es.1_account_common_4300")
        self.partner_id = self.ref("somconnexio.res_partner_1_demo")
        self.product_id = self.ref("somconnexio.SenseMinutsSenseDades")
        self.journal_id = self.ref(
            "invoice_somconnexio.customer_services_invoices_journal"
        )
        self.income_account = self.env["account.account"].search(
            [("account_type", "=", "income"), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        self.account_move_data = {
            "partner_id": self.partner_id,
            "move_type": "out_invoice",
            "payment_mode_id": self.inbound_mode.id,
            "journal_id": self.journal_id,
        }
        self.account_move_line_data = {
            "product_id": self.partner_id,
            "quantity": 1.0,
            "price_unit": 100.0,
            "name": "product that cost 100",
            "account_id": self.income_account.id,
        }

    def test_creation_payment_with_consumption_invoice(self):
        invoice = self.env["account.move"].create(self.account_move_data)
        account_move_line_data = self.account_move_line_data.copy()
        account_move_line_data.update(
            {
                "move_id": invoice.id,
            }
        )
        self.env["account.move.line"].create(account_move_line_data)
        invoice.action_post()

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({}).run()
        payment_order = self.inbound_order
        payment_order.draft2open()
        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(payment_order.payment_line_ids.purpose, "PHON")

    def test_creation_payment_without_consumption_invoice(self):
        account_move_data = self.account_move_data.copy()
        account_move_data.pop("journal_id")
        invoice = self.env["account.move"].create(account_move_data)
        account_move_line_data = self.account_move_line_data.copy()
        account_move_line_data.update(
            {
                "move_id": invoice.id,
            }
        )
        self.env["account.move.line"].create(account_move_line_data)
        invoice.action_post()

        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({}).run()
        payment_order = self.inbound_order
        payment_order.draft2open()
        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertFalse(payment_order.payment_line_ids.purpose)
