from odoo.addons.account.tests.common import TransactionCase
from odoo.tests import tagged
from odoo import fields
from odoo.exceptions import UserError
from odoo import Command


@tagged("post_install", "-at_install")
class AccountInvoiceTestCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.account_invoice_obj = self.env["account.move"]
        self.payment_term = self.env.ref("account.account_payment_term_advance")
        self.partner = self.env.ref("somconnexio.res_partner_2_demo")
        self.product = self.env.ref("somconnexio.SenseMinutsSenseDades")
        self.quantity = 1
        self.price_unit = 12.0
        self.account_income = self.env["account.account"].search(
            [
                ("account_type", "=", "income"),
                ("company_id", "=", self.env.user.company_id.id),
            ],
            limit=1,
        )
        self.journalrec = self.browse_ref("somconnexio.consumption_invoices_journal")

        self.account_invoice_customer0 = self.env.ref(
            "invoice_somconnexio.invoice_bi_demo"
        )

    def test_set_cooperator_effective_in_partner_with_share_lines_not_have_effects(
        self,
    ):  # noqa
        share_product = self.browse_ref(
            "cooperator_somconnexio.cooperator_share_product"
        ).product_variant_id
        partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.env["share.line"].create(
            {
                "share_number": 1,
                "share_product_id": share_product.id,
                "partner_id": partner.id,
                "share_unit_price": share_product.lst_price,
                "effective_date": fields.Date.today(),
            }
        )
        invoice = self.env["account.move"].create(
            {
                "partner_id": partner.id,
            }
        )

        invoice.set_cooperator_effective(None)

        self.assertEqual(len(partner.share_ids), 1)

    def test_customer_invoice(self):
        # I check that Initially customer invoice is in the "Draft" state
        self.assertEqual(self.account_invoice_customer0.state, "draft")

        # I validate invoice by creating on
        self.account_invoice_customer0.action_post()

        # I check that the invoice state is "Open"
        self.assertEqual(self.account_invoice_customer0.state, "posted")

    def test_customer_invoice_archived_journal(self):
        # I check that Initially customer invoice is in the "Draft" state
        self.assertEqual(self.account_invoice_customer0.state, "draft")

        archived_journal = self.env["account.journal"].create(
            {
                "name": "Test Archived Journal",
                "code": "TEST",
                "type": "sale",
                "refund_sequence": True,
                "default_account_id": self.account_income.id,
                "default_expense_account_id": self.account_income.id,
                "sequence": 10,
                "active": False,
            }
        )
        self.account_invoice_customer0.journal_id = archived_journal
        # I validate invoice by creating on
        self.assertRaises(UserError, self.account_invoice_customer0.action_post)

    def test_create_right_regular_invoice(self):
        tax_id = (
            self.env["account.tax"]
            .search(
                [
                    ("name", "=", "IVA 21% (Servicios)"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            .id
        )
        invoice_line_params = {
            "name": self.product.name,
            "product_id": self.product.id,
            "quantity": self.quantity,
            "price_unit": self.price_unit,
            "account_id": self.account_income.id,
            "tax_ids": [
                Command.link(tax_id),
            ],
        }
        invoice_params = {
            "partner_id": self.partner.id,
            "invoice_date": "2024-01-12",
            "line_ids": [
                Command.create(invoice_line_params),
            ],
        }
        invoice = self.account_invoice_obj.create(invoice_params)
        invoice.action_post()
        self.assertEqual(self.product, invoice.invoice_line_ids[0].product_id)
        self.assertEqual(
            self.quantity * self.price_unit, invoice.invoice_line_ids[0].price_subtotal
        )
        self.assertEqual(
            (self.quantity * self.price_unit) * 1.21,
            invoice.invoice_line_ids[0].price_total,
        )
        self.assertEqual(self.account_income, invoice.invoice_line_ids[0].account_id)
        # TODO: Check taxes in Odoo 16
        # self.assertEqual(
        #    (self.quantity * self.price_unit) * 0.21,
        #    invoice.amount_tax,
        # )
        # self.assertEqual(invoice.amount_untaxed, self.quantity * self.price_unit)
        # self.assertEqual(
        #     invoice.amount_total,
        #     (self.quantity * self.price_unit) * 1.21
        # )
