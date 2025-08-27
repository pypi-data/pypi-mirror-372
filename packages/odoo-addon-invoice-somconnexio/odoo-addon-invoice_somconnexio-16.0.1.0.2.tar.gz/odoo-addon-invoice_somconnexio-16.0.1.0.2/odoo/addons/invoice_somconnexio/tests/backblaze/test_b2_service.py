import os
from mock import patch

from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase

from ...backblaze.b2_service import B2Service

EXPECTED_APPLICATION_KEY_ID = "APPLICATION_KEY_ID"
EXPECTED_APPLICATION_KEY = "APPLICATION_KEY"


@patch.dict(
    os.environ,
    {
        "INVOICE_B2_APPLICATION_KEY_ID": EXPECTED_APPLICATION_KEY_ID,
        "INVOICE_B2_APPLICATION_KEY": EXPECTED_APPLICATION_KEY,
    },
)
class B2ServiceTestCase(SCTestCase):
    @patch("odoo.addons.invoice_somconnexio.backblaze.b2_service.base64")
    @patch("odoo.addons.invoice_somconnexio.backblaze.b2_service.BytesIO")
    @patch(
        "odoo.addons.invoice_somconnexio.backblaze.b2_service.DoNothingProgressListener"  # noqa
    )
    @patch("odoo.addons.invoice_somconnexio.backblaze.b2_service.AuthInfoCache")
    @patch(
        "odoo.addons.invoice_somconnexio.backblaze.b2_service.InMemoryAccountInfo"  # noqa
    )
    @patch("odoo.addons.invoice_somconnexio.backblaze.b2_service.B2Api")
    def test_get_pdf_invoice(
        self,
        B2ApiMock,
        InMemoryAccountInfoMock,
        AuthInfoCacheMock,
        DoNothingProgressListener,
        BytesIOMock,
        base64Mock,
    ):
        file_id = "example_file_id"

        B2Service().get_pdf_invoice(file_id)

        AuthInfoCacheMock.assert_called_once_with(
            InMemoryAccountInfoMock.return_value,
        )
        B2ApiMock.assert_called_once_with(
            InMemoryAccountInfoMock.return_value, cache=AuthInfoCacheMock.return_value
        )
        B2ApiMock.return_value.authorize_account.assert_called_once_with(
            "production",
            EXPECTED_APPLICATION_KEY_ID,
            EXPECTED_APPLICATION_KEY,
        )
        B2ApiMock.return_value.download_file_by_id.assert_called_once_with(
            file_id, DoNothingProgressListener.return_value
        )
        B2ApiMock.return_value.download_file_by_id.return_value.save.assert_called_once_with(  # noqa
            BytesIOMock.return_value
        )
        BytesIOMock.return_value.seek.assert_called_once_with(0)
        BytesIOMock.return_value.read.assert_called_once_with()
        base64Mock.b64encode.assert_called_once_with(
            BytesIOMock.return_value.read.return_value
        )
        base64Mock.b64encode.return_value.decode.assert_called_once_with("utf-8")
