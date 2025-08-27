from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class SendTokenizedInvoiceTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.invoice = self.browse_ref("invoice_somconnexio.invoice_bi_demo")

    @patch(
        "odoo.addons.invoice_somconnexio.models.send_tokenized_invoice.SomOfficeUser"
    )
    def test_send_tokenized_invoice(self, SomOfficeUserMock):
        self.invoice.company_id.customer_invoice_mail_template_id = self.env.ref(
            "account.email_template_edi_invoice"
        )

        SomOfficeUserMock.return_value.generate_invoice_token.return_value = {
            "invoice_token": "token"
        }

        self.env["send.tokenized.invoice"].send_tokenized_invoice(self.invoice)

        SomOfficeUserMock.assert_called_once_with(
            self.invoice.partner_id.ref,
            self.invoice.partner_id.email,
            self.invoice.partner_id.vat,
            self.invoice.partner_id.lang,
            self.env,
        )
        SomOfficeUserMock.return_value.generate_invoice_token.assert_called_once_with(
            self.invoice.id
        )
