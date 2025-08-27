S_PAGING_RETURN = {
    "limit": {"type": "integer"},
    "offset": {"type": "integer"},
    "totalNumberOfRecords": {"type": "integer"},
    "sortBy": {"type": "string"},
    "sortOrder": {"type": "string"},
}

S_PAGING = {
    "limit": {
        "type": "string",
    },
    "offset": {
        "type": "string",
    },
    "sortBy": {
        "type": "string",
    },
    "sortOrder": {"type": "string", "dependencies": ["sortBy"]},
}

S_INVOICE_SEARCH = {
    "customer_ref": {
        "type": "string",
        "excludes": ["partner_vat"],
        "required": True,
    },
    "partner_vat": {
        "type": "string",
        "excludes": ["customer_ref"],
        "required": True,
    },
    **S_PAGING,
}

S_INVOICE_RETURN = {
    "id": {"type": "integer", "required": True},
    "name": {"type": "string", "required": True, "empty": False},
    "date": {"type": "string", "required": True, "empty": False},
    "total_amount": {"type": "float", "required": True},
    "tax_amount": {"type": "float", "required": True},
    "base_amount": {"type": "float", "required": True},
    "status": {"type": "string", "required": True},
}

S_INVOICE_RETURN_GET = {
    "pdf": {"type": "string", "required": True, "empty": False},  # TODO review
    **S_INVOICE_RETURN,
}

S_INVOICE_RETURN_SEARCH = {
    "invoices": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": S_INVOICE_RETURN,
        },
        "required": True,
    },
    "paging": {"type": "dict", "schema": S_PAGING_RETURN},
}

S_ACCOUNT_INVOICE_CREATE = {
    "groupCode": {"type": "string", "required": True, "regex": "^[0-9]+(_[0-9]*)+"},
    "id_billing_run": {"type": "string", "required": True},
    "invoiceDate": {
        "type": "integer",
        "required": True,
    },
    "invoiceLines": {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": {
                "description": {"type": "string", "required": True},
                "accountingCode": {"type": "string", "required": True},
                "amountWithoutTax": {"type": "float", "required": True},
                "amountWithTax": {"type": "float", "required": True},
                "amountTax": {"type": "float", "required": True},
                "taxCode": {"type": "string", "required": True},
                "productCode": {"type": "string", "required": True},
            },
        },
    },
    "odoo_contracts": {"type": "string"},
}
