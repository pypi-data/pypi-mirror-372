import logging

try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

from . import schemas
from odoo import _
from werkzeug.exceptions import BadRequest
from odoo.exceptions import UserError
from datetime import datetime

_logger = logging.getLogger(__name__)


class AccountInvoiceProcess:
    def __init__(self, env=False):
        self.env = env

    # pylint: disable=method-required-super
    def create(self, **params):
        v = Validator(purge_unknown=True)
        if not v.validate(
            params,
            self._validator_create(),
        ):
            raise UserError(_(f"BadRequest {v.errors}"))

        lines_params = params["invoiceLines"]
        params = self._prepare_create(params)
        # tracking_disable=True in context is needed
        # to avoid to send a mail in Account Invoice creation
        invoice = (
            self.env["account.move"].with_context(tracking_disable=True).create(params)
        )
        self.create_invoice_lines(invoice, lines_params)
        return self._to_dict(invoice)

    def create_invoice_lines(self, invoice, lines_params):
        invoice_lines = [line for line in lines_params if line.get("amountWithoutTax")]
        for line in invoice_lines:
            self._create_line(line, invoice).id

    def _prepare_create_line(self, line, invoice):
        account = self.env["account.account"].search(
            [("code", "=", line["accountingCode"])]
        )
        if not account:
            raise BadRequest(f"Account code {line['accountingCode']} not found")
        tax = self.env["account.tax"].search(
            [
                ("oc_code", "=", line["taxCode"]),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        if not tax:
            raise BadRequest(f"Tax code {line['taxCode']} not found")

        product = self.env["product.product"].search(
            [("default_code", "=", line["productCode"])]
        )
        if not product:
            raise BadRequest(f"Product with code {line['productCode']} not found")
        response_line = {
            "name": line["description"],
            "move_id": invoice.id,
            "account_id": account.id,
            "price_subtotal": line["amountWithoutTax"],
            "price_total": line["amountWithTax"],
            "tax_ids": [(4, tax.id)],
            "product_id": product.id,
            "price_unit": line["amountWithoutTax"],
        }
        return response_line

    def _prepare_create(self, params):
        invoice_date = datetime.fromtimestamp(int(params["invoiceDate"])).date()
        journal_id = self.env.ref(
            "invoice_somconnexio.customer_services_invoices_journal"
        ).id
        group_code = params["groupCode"]
        contract_group = self.env["contract.group"].search([("code", "=", group_code)])
        if not contract_group:
            raise BadRequest(f"Group with code {group_code} not found")
        if not contract_group.partner_id:
            raise BadRequest(f"Group {group_code} without partner related")
        if self.env["account.move"].search(
            [
                ("invoice_date", "=", invoice_date),
                ("contract_group_id", "=", contract_group.id),
                ("journal_id", "=", journal_id),
            ]
        ):
            raise UserError(
                _(
                    f"Duplicated invoice for group {contract_group.code} and date {invoice_date}"  # noqa
                )
            )
        partner = contract_group.partner_id
        partner_id = partner.id
        first_contract = self._get_odoo_first_contracts(
            params["invoiceLines"][0]["odoo_contracts"]
        )
        return {
            "partner_id": partner_id,
            "invoice_date": invoice_date,
            "journal_id": journal_id,
            "contract_group_id": contract_group.id,
            "billing_run_id": params["id_billing_run"],
            "payment_mode_id": contract_group.contract_ids[0].payment_mode_id.id,
            "mandate_id": first_contract.mandate_id.id,
            "emails": ",".join(first_contract.email_ids.mapped("email")),
            "move_type": "out_invoice",
        }

    def _create_line(self, line, invoice):
        invoice_line = self.env["account.move.line"].create(
            self._prepare_create_line(line, invoice)
        )
        contracts = self._get_odoo_contracts(line["odoo_contracts"])
        self.env["contract.account.invoice.line.relation"].create(
            [
                {
                    "account_invoice_line_id": invoice_line.id,
                    "contract_id": contract.id,
                }
                for contract in contracts
            ]
        )
        return invoice_line

    def _validator_create(self):
        return schemas.S_ACCOUNT_INVOICE_CREATE

    @staticmethod
    def _to_dict(account_invoice):
        return {"id": account_invoice.id}

    def _get_odoo_contracts(self, contracts):
        contract_codes = contracts.split("|")
        contracts = (
            self.env["contract.contract"]
            .sudo()
            .search([("code", "in", contract_codes)])
        )
        return contracts

    def _get_odoo_first_contracts(self, contracts):
        contract_code = contracts.split("|")[0]
        contract = (
            self.env["contract.contract"].sudo().search([("code", "=", contract_code)])
        )
        return contract
