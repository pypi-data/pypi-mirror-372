from odoo.tests.common import Form, TransactionCase
from mock import patch
from datetime import date


class TestPaymentReturn(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        journal = cls.env.ref("invoice_somconnexio.customer_services_invoices_journal")
        partner_expense = cls.env["res.partner"].create({"name": "PE"})
        cls.bank_journal = cls.env.ref("somconnexio.caixa_guissona_journal")
        cls.bank_journal.write(
            {
                "default_expense_partner_id": partner_expense.id,
            }
        )
        income_account = cls.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_id", "=", cls.env.user.company_id.id),
            ],
            limit=1,
        )
        cls.partner = cls.env.ref("somconnexio.res_partner_1_demo")
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "journal_id": journal.id,
                "company_id": cls.env.user.company_id.id,
                "currency_id": cls.env.user.company_id.currency_id.id,
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": income_account.id,
                            "name": "Test line",
                            "price_unit": 50,
                            "quantity": 10,
                            "tax_ids": False,
                        },
                    )
                ],
            }
        )
        cls.reason = cls.env["payment.return.reason"].create(
            {"code": "RTEST", "name": "Reason Test"}
        )
        cls.invoice.action_post()
        cls.receivable_line = cls.invoice.line_ids.filtered(
            lambda x: x.account_id.account_type == "asset_receivable"
        )
        # Create payment from invoice
        cls.payment_register_model = cls.env["account.payment.register"]
        payment_register = Form(
            cls.payment_register_model.with_context(
                active_model="account.move", active_ids=cls.invoice.ids
            )
        )
        cls.payment = payment_register.save()._create_payments()
        cls.payment_move = cls.payment.move_id
        cls.payment_line = cls.payment_move.line_ids.filtered(
            lambda x: x.account_id.account_type == "asset_receivable"
        )
        account = cls.env["account.account"].search(
            [
                ("account_type", "=", "asset_receivable"),
                ("company_id", "=", cls.env.user.company_id.id),
                ("reconcile", "=", True),
            ],
            limit=1,
        )
        # Create payment return
        cls.payment_return = cls.env["payment.return"].create(
            {
                "journal_id": cls.bank_journal.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.partner.id,
                            "move_line_ids": [(6, 0, cls.payment_line.ids)],
                            "amount": cls.payment_line.credit,
                            "expense_account": account.id,
                            "expense_amount": 10.0,
                            "expense_partner_id": cls.partner.id,
                        },
                    )
                ],
            }
        )

    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_activity_creation_type_1_when_returned_payment(self, send_mail_mock):
        self.payment_return.action_draft()
        self.payment_return.action_confirm()
        activity_type_1 = self.ref("somconnexio.return_activity_type_1")
        account_invoice_model = self.env["ir.model"].search(
            [("model", "=", "account.move")]
        )
        # TODO: Review the limit=1. Why are two activities created?
        activity = self.env["mail.activity"].search(
            [
                ("res_id", "=", self.invoice.id),
                ("res_model_id", "=", account_invoice_model.id),
                ("activity_type_id", "=", activity_type_1),
            ],
            limit=1,
        )
        self.assertTrue(activity)
        self.assertEqual(activity.date_done, date.today())
        send_mail_mock.assert_called_with(
            self.invoice.id,
            False,
        )

    def test_activity_creation_type_n_when_returned_payment_again(self):
        self.invoice.returned_payment = True
        self.payment_return.action_draft()
        self.payment_return.action_confirm()
        activity_type_n = self.ref("somconnexio.return_activity_type_n")
        account_invoice_model = self.env["ir.model"].search(
            [("model", "=", "account.move")]
        )
        self.assertTrue(
            self.env["mail.activity"].search(
                [
                    ("res_id", "=", self.invoice.id),
                    ("res_model_id", "=", account_invoice_model.id),
                    ("activity_type_id", "=", activity_type_n),
                ]
            )
        )

    def test_find_match_move_line(self):
        self.payment_return.journal_id = self.bank_journal
        self.payment_line.name = "test match move line L12010"
        self.payment_return.write(
            {
                "line_ids": [
                    (5, 0, 0),
                    (
                        0,
                        0,
                        {
                            "partner_id": False,
                            "move_line_ids": [(6, 0, [])],
                            "amount": 0.0,
                            "reference": "L12010",
                        },
                    )
                ]
            }
        )
        self.payment_return.button_match()
        self.assertEqual(
            self.payment_return.line_ids[0].move_line_ids, self.payment_line
        )

    def test_find_match_move_line_different_reference(self):
        self.payment_return.journal_id = self.bank_journal
        self.payment_line.ref = "test match move line L12001"
        self.payment_return.write(
            {
                "line_ids": [
                    (5, 0, 0),
                    (
                        0,
                        0,
                        {
                            "partner_id": False,
                            "move_line_ids": [(6, 0, [])],
                            "amount": 0.0,
                            "reference": "L12010",
                        },
                    )
                ]
            }
        )
        self.payment_return.button_match()
        self.assertFalse(self.payment_return.line_ids[0].move_line_ids)

    def test_account_move_last_return_amount(self):
        self.payment_return.journal_id = self.bank_journal
        self.payment_line.name = "test match move line L12010"
        self.payment_return.write(
            {
                "line_ids": [
                    (5, 0, 0),
                    (
                        0,
                        0,
                        {
                            "partner_id": False,
                            "move_line_ids": [(6, 0, [])],
                            "amount": 0.0,
                            "reference": "L12010",
                        },
                    ),
                ]
            }
        )
        self.payment_return.button_match()
        self.payment_return.action_confirm()
        account_move = self.payment_return.line_ids[0].move_line_ids.move_id
        self.assertEqual(account_move.last_return_amount, self.payment_line.credit)
        self.assertEqual(account_move.payment_state, "not_paid")
