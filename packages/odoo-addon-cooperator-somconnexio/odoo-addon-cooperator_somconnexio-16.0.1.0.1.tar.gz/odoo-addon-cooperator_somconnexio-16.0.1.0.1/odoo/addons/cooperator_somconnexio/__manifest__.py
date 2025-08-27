{
    "version": "16.0.1.0.1",
    "name": "Cooperator - SomConnexio",
    "summary": """
        SomConnexio custom usage of cooperative users (cooperators).
    """,
    "depends": [
        "somconnexio",
        "cooperator_sponsorship",
        "l10n_es_cooperator",
    ],
    "external_dependencies": {
        "python": ["faker"],
    },
    "author": """
        Som Connexió SCCL,
        Coopdevs Treball SCCL,
    """,
    "category": "Cooperative Management",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "data": [
        "data/account_payment_term.xml",
        "data/discovery_channel.xml",
        "data/mail_activity_type.xml",
        "data/operation_request_terminate_reason.xml",
        "data/share_type.xml",
        "security/ir.model.access.csv",
        "reports/sponsor_sell_back_template.xml",
        "reports/crm_lead_creation_email_template.xml",
        "reports/crm_lead_creation_manual_email_template.xml",
        # "reports/crm_lead_creation_CM_email_template.xml",
        "views/coop_agreement_view.xml",
        "views/crm_lead_line.xml",
        "views/crm_lead.xml",
        "views/operation_request.xml",
        "views/menus.xml",
        "views/res_partner_view.xml",
        "views/subscription_request_view.xml",
        "wizards/create_subscription_from_partner/create_subscription_from_partner.xml",
    ],
    "demo": [
        "demo/partner.xml",
        "demo/subscription_requests.xml",
    ],
    "application": False,
    "installable": True,
}
