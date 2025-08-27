import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "external_dependencies_override": {
            "python": {
                "otrs_somconnexio": "otrs-somconnexio==0.6.5",
            },
        },
    },
)
