{
    "name": "Odoo Som Connexió OTRS integration",
    "version": "16.0.1.0.9",
    "depends": [
        "somconnexio",
        "switchboard_somconnexio",
        "delivery_somconnexio",
        "contract_api_somconnexio",
    ],
    "external_dependencies": {
        "python": ["otrs_somconnexio"],
    },
    "author": "Coopdevs Treball SCCL, " "Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "category": "Cooperative management",
    "license": "AGPL-3",
    "data": [
        "crons/activate_change_tariff_OTRS_tickets_cron.xml",
        "wizards/contract_address_change/contract_address_change.xml",
        "wizards/contract_mobile_tariff_change/contract_mobile_tariff_change.xml",
        "views/broadband_isp_info_view.xml",
        "views/contract_view.xml",
        "views/crm_lead_line_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
