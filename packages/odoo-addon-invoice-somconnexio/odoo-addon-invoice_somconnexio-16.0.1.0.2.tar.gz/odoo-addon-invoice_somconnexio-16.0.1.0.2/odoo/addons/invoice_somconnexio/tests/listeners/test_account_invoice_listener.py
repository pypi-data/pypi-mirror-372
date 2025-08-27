from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase


class TestAccountInvoiceListener(SCComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceListener, cls).setUpClass()
        cls.setUpComponent()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=False,
            )
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.invoice = self.env.ref("invoice_somconnexio.invoice_bi_demo")

    @patch(
        "odoo.addons.invoice_somconnexio.listeners.account_invoice.NotifyInvoiceNumber"
    )
    def test_invoice_date_number_notify_BI_API(self, NotifyInvoiceNumberMock):
        self.invoice.b2_file_id = False
        self.invoice.action_post()
        NotifyInvoiceNumberMock.assert_called_once_with(self.invoice.name)
        NotifyInvoiceNumberMock.return_value.run.assert_called_once()

    @patch(
        "odoo.addons.invoice_somconnexio.listeners.account_invoice.NotifyInvoiceNumber"
    )
    def test_not_invoice_date_number_notify_BI_API_when_has_b2_file_id(
        self, NotifyInvoiceNumberMock
    ):
        self.invoice.action_post()

        NotifyInvoiceNumberMock.assert_not_called()
