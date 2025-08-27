from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class DownloadInvoiceTestCase(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.invoice = self.browse_ref("invoice_somconnexio.invoice_bi_demo")
        self.invoice_oc = self.browse_ref("invoice_somconnexio.invoice_oc_demo")

    @patch("odoo.addons.invoice_somconnexio.models.download_invoice.B2Service")
    def test_download_invoice_pdf_from_b2(self, B2ServiceMock):
        B2ServiceMock.return_value.get_pdf_invoice.return_value = "fake_b64_invoice"
        invoice_pdf_base64 = self.env["download.invoice"].download_invoice_pdf(
            self.invoice.name
        )

        self.assertEqual(
            B2ServiceMock.return_value.get_pdf_invoice.return_value,
            invoice_pdf_base64,
        )
        B2ServiceMock.return_value.get_pdf_invoice.assert_called_with(
            self.invoice.b2_file_id
        )

    @patch("odoo.addons.invoice_somconnexio.models.download_invoice.Invoice")
    def test_download_invoice_pdf_from_OC(self, InvoiceOCMock):
        expected_invoice_pdf_base64 = "fake_b64_invoice"
        InvoiceOCMock.getInvoicePdfByNumber.return_value = expected_invoice_pdf_base64
        invoice_pdf_base64 = self.env["download.invoice"].download_invoice_pdf(
            self.invoice_oc.name
        )

        self.assertEqual(
            invoice_pdf_base64,
            expected_invoice_pdf_base64,
        )
        InvoiceOCMock.getInvoicePdfByNumber.assert_called_once_with(
            self.invoice_oc.name
        )
