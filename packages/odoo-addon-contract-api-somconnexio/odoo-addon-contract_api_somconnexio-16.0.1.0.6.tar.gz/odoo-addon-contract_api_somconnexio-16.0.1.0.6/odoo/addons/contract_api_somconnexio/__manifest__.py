{
    "version": "16.0.1.0.6",
    "name": "Contract API - SomConnexio",
    "summary": """
    Expose the REST API used in Som Connexió to create and manage contracts in Odoo.
    """,
    "author": """
        Som Connexió SCCL,
        Coopdevs Treball SCCL
    """,
    "category": "Cooperative Management",
    "website": "https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio",
    "license": "AGPL-3",
    "depends": [
        "contract_group_somconnexio",
        "res_partner_api_somconnexio",
        "switchboard_somconnexio",
        "somconnexio",
    ],
    "external_dependencies": {
        "python": ["faker"],
    },
    "application": False,
    "installable": True,
}
