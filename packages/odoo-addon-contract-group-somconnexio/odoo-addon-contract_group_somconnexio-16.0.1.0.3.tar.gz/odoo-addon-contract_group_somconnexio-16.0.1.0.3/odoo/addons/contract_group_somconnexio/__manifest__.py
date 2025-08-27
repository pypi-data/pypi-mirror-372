{
    "name": "Odoo Som Connexió contract group customizations",
    "version": "16.0.1.0.3",
    "depends": [
        "contract_group",
        "somconnexio",
    ],
    "author": "Coopdevs Treball SCCL,Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "category": "Cooperative management",
    "license": "AGPL-3",
    "data": [
        "wizards/contract_group_change/contract_group_change.xml",
        "wizards/contract_iban_change/contract_iban_change.xml",
        "wizards/partner_email_change/partner_email_change.xml",
        "views/account_move.xml",
        "views/contract.xml",
        "data/contract_group.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/contract_group.xml",
    ],
    "external_dependencies": {},
}
