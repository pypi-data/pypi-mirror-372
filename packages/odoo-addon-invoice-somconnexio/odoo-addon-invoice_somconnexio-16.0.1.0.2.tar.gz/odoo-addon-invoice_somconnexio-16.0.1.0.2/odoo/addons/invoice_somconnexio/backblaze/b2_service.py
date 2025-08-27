from b2sdk.v2 import (
    InMemoryAccountInfo,
    AuthInfoCache,
    B2Api,
    DoNothingProgressListener,
)
import os
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class B2Service:
    def __init__(self):
        self.application_key_id = os.getenv("INVOICE_B2_APPLICATION_KEY_ID")
        self.application_key = os.getenv("INVOICE_B2_APPLICATION_KEY")
        if not self.application_key_id or not self.application_key:
            logger.error(
                "B2 application key id or key not found. Please check the environment variables"  # noqa
            )

    def get_pdf_invoice(self, file_id):
        file_contents_io = BytesIO()
        info = InMemoryAccountInfo()
        progress_listener = DoNothingProgressListener()

        b2_api = B2Api(info, cache=AuthInfoCache(info))
        b2_api.authorize_account(
            "production", self.application_key_id, self.application_key
        )
        downloaded_file = b2_api.download_file_by_id(file_id, progress_listener)
        downloaded_file.save(file_contents_io)
        file_contents_io.seek(0)

        # Obtener el contenido del archivo en bytes
        file_contents = file_contents_io.read()

        # Codificar el contenido del archivo en base64
        return base64.b64encode(file_contents).decode("utf-8")
