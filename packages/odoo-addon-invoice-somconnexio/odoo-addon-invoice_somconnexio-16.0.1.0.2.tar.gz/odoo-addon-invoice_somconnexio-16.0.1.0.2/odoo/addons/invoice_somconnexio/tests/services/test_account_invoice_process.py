from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from datetime import datetime
from ...services.account_invoice_process import (
    AccountInvoiceProcess,
)
from werkzeug.exceptions import BadRequest
from odoo.exceptions import UserError


class InvoiceProcessCase(SCTestCase):
    def setUp(self):
        super().setUp()
        self.process = AccountInvoiceProcess(self.env)
        self.invoice_date = datetime(2021, 1, 31)
        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.contract_group = self.browse_ref(
            "contract_group_somconnexio.contract_group_1"
        )
        self.partner.ref = "12345"
        self.billing_run_id = "123545-42342kjhnk23j4-asfewfvsa34sa"
        self.product = self.browse_ref("somconnexio.Fibra100Mb")
        self.price_unit = 41
        self.quantity = 1
        self.account = self.env["account.account"].search([("code", "=", "43000000")])
        self.account_taxes = self.env["account.account"].search(
            [("code", "=", "47700000")]
        )
        self.oc_amount_untaxed = 10.0
        self.oc_amount_taxes = 2.1
        self.tax = self.env["account.tax"].search(
            [
                ("name", "=", "IVA 21% (Servicios)"),
                ("company_id", "=", self.env.user.company_id.id),
            ]
        )
        self.account_tax_group = self.env["account.tax.group"].search(
            [("name", "=", "IVA 21%")]
        )
        self.tax.oc_code = "TAX_HIGH"
        self.landline_account = self.browse_ref("somconnexio.account_sc_70500020")
        self.mobile_account = self.browse_ref("somconnexio.account_sc_70500010")
        self.journal_id = self.browse_ref(
            "invoice_somconnexio.customer_services_invoices_journal"
        )
        self.data = {
            "groupCode": self.contract_group.code,
            "id_billing_run": self.billing_run_id,
            "invoiceDate": int(self.invoice_date.timestamp()),
            "invoiceLines": [
                {
                    "accountingCode": "70500010",
                    "description": "Consum de dades incloses a l'abonament",
                    "taxCode": "TAX_HIGH",
                    "amountWithoutTax": 1.0000000000,
                    "amountWithTax": 1.210000000000,
                    "amountTax": 0.21,
                    "productCode": self.product.default_code,
                    "odoo_contracts": self.contract_group.contract_ids[0].code,
                }
            ],
        }

    def test_right_create(self):
        content = self.process.create(**self.data)
        self.assertIn("id", content)
        invoice = self.env["account.move"].browse(content["id"])
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertEqual(invoice.invoice_date, self.invoice_date.date())
        self.assertEqual(invoice.billing_run_id, self.billing_run_id)
        self.assertEqual(
            invoice.payment_mode_id, self.contract_group.contract_ids[0].payment_mode_id
        )
        self.assertEqual(
            invoice.mandate_id, self.contract_group.contract_ids[0].mandate_id
        )
        self.assertEqual(invoice.journal_id, self.journal_id)
        self.assertEqual(
            invoice.emails,
            ",".join(self.contract_group.contract_ids[0].email_ids.mapped("email")),
        )

    def test_route_wrong_create_bad_account_code(self):
        data = self.data.copy()
        data.update(
            {
                "groupCode": "XXX_0",
            }
        )
        self.assertRaises(UserError, self.process.create, **data)

    def test_route_wrong_create_partner_not_found(self):
        data = self.data.copy()
        data.update(
            {
                "groupCode": "0_0",
            }
        )
        self.assertRaises(BadRequest, self.process.create, **data)

    def test_route_wrong_create_missing_partner_id(self):
        data = self.data.copy()
        del data["groupCode"]
        self.assertRaises(UserError, self.process.create, **data)

    def test_route_wrong_create_missing_invoice_date(self):
        data = self.data.copy()
        del data["invoiceDate"]
        self.assertRaises(UserError, self.process.create, **data)

    def test_route_right_create_invoice_lines(self):
        data = self.data.copy()
        data.update(
            {
                "invoiceLines": [
                    {
                        "accountingCode": "70500010",
                        "description": "Consum de dades incloses a l'abonament",
                        "taxCode": "TAX_HIGH",
                        "amountWithoutTax": 1.0000000000,
                        "amountWithTax": 1.210000000000,
                        "amountTax": 0.21,
                        "productCode": "ISCAT_SC_CONSUMPTION_SMS_NAC",
                        "odoo_contracts": self.contract_group.contract_ids[0].code,
                    },
                    {
                        "accountingCode": "70500010",
                        "description": "Consum de dades incloses a l'abonament",
                        "taxCode": "TAX_HIGH",
                        "amountWithoutTax": 10.0000000000,
                        "amountWithTax": 12.10000000000,
                        "amountTax": 0.21,
                        "productCode": "ISCAT_SC_CONSUMPTION_DATA_NAC_INC",
                        "odoo_contracts": self.contract_group.contract_ids[0].code,
                    },
                ]
            }
        )
        content = self.process.create(**data)
        self.assertIn("id", content)
        invoice = self.env["account.move"].browse(content["id"])
        self.assertEqual(invoice.partner_id, self.partner)
        self.assertEqual(invoice.invoice_date, self.invoice_date.date())
        self.assertEqual(invoice.journal_id, self.journal_id)
        self.assertTrue(invoice.invoice_line_ids)
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        self.assertEqual(1.0, invoice.invoice_line_ids[0].price_subtotal)
        self.assertEqual(1.21, invoice.invoice_line_ids[0].price_total)
        self.assertEqual(len(invoice.invoice_line_ids[0].tax_ids), 1)
        self.assertEqual(invoice.invoice_line_ids[0].tax_ids[0], self.tax)
        # self.assertEqual(invoice.tax_line_ids[0].tax_id, self.tax)
        # self.assertEqual(invoice.tax_line_ids[0].amount, 2.31)
        self.assertEqual(
            invoice.invoice_line_ids[0].product_id,
            self.env["product.product"].search(
                [("default_code", "=", "ISCAT_SC_CONSUMPTION_SMS_NAC")]
            ),
        )

    def test_route_bad_subcategory_code(self):
        data = self.data.copy()
        invoice_line = data["invoiceLines"][0]
        invoice_line["productCode"] = "XXX"
        data["invoiceLines"] = [invoice_line]

        self.assertRaises(BadRequest, self.process.create, **data)

    def test_route_bad_tax_line(self):
        data = self.data.copy()
        invoice_line = data["invoiceLines"][0]
        invoice_line["taxCode"] = "XXX"
        data["invoiceLines"] = [invoice_line]
        self.assertRaises(BadRequest, self.process.create, **data)

    def test_route_wrong_duplicate(self):
        self.process.create(**self.data)
        self.assertRaises(UserError, self.process.create, **self.data)

    def test_route_right_create_contract_account_invoice_lines_relation(self):
        content = self.process.create(**self.data)
        invoice = self.env["account.move"].browse(content["id"])
        contract_invoice_lines_relation = self.env[
            "contract.account.invoice.line.relation"
        ].search([("account_invoice_line_id", "in", invoice.invoice_line_ids.ids)])
        self.assertEqual(len(contract_invoice_lines_relation), 1)
        self.assertEqual(
            contract_invoice_lines_relation.contract_id,
            self.contract_group.contract_ids[0],
        )
        self.assertEqual(
            contract_invoice_lines_relation.account_invoice_line_id,
            invoice.invoice_line_ids,
        )
        # self.assertEqual(
        #    self.contract_group.contract_ids[0].invoice_count,
        #    1,
        # )
