{
    "name": "filmin_somconnexio",
    "version": "16.0.1.0.3",
    "depends": ["multimedia_somconnexio"],
    "summary": """
        Manages filmin subscriptions within the SomConnexio ERP
    """,
    "author": "Coopdevs Treball SCCL, " "Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "category": "Cooperative management",
    "data": [
        "data/service_supplier.xml",
        "data/sale_subscription_template.xml",
        "data/service_technology_service_supplier.xml",
        "data/product_category_technology_supplier_data.xml",
        "data/product_product.xml",
        "views/contract_views.xml",
        "reports/crm_lead_creation_email_template.xml",
        "reports/crm_lead_creation_manual_email_template.xml",
    ],
    "demo": [
        "demo/stock_lot.xml",
        "demo/contract.xml",
    ],
    "post_init_hook": "_demo_stock_lots_move",
}
