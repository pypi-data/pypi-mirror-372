{
    "name": "invoice Som Connexió module",
    "version": "16.0.1.0.2",
    "depends": [
        "somconnexio",
        "contract_group_somconnexio",
        "cooperator_somconnexio",
        "queue_job",
        "account",
        "base_rest",
        "account_payment_partner",
        "account_payment_order",
    ],
    "external_dependencies": {
        "python": [
            "b2sdk",
            "bi_sc_client",
            "pyopencell",
        ],
    },
    "author": "Coopdevs Treball SCCL, " "Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "category": "Cooperative management",
    "license": "AGPL-3",
    "data": [
        "data/account_journal.xml",
        "views/account_invoice.xml",
        "views/res_company.xml",
        # TODO: Is this view needed?
        # "views/account_payment_order_view.xml",
        "wizards/account_invoice_confirm_between_dates/account_invoice_confirm_between_dates.xml",  # noqa
        "wizards/contract_invoice_payment/contract_invoice_payment.xml",
        "wizards/invoice_claim_1_send/invoice_claim_1_send.xml",
        "wizards/payment_order_confirm/payment_order_confirm.xml",
        "wizards/payment_order_generated_to_uploaded_queued/payment_order_generated_to_uploaded_queued.xml",  # noqa
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/invoice.xml",
    ],
}
