{
    "name": "Product Testing",
    "summary": "Manage product testing stages and tester issues",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/testing_stage_data.xml",
        "report/testing_product_report.xml",
        "report/testing_product_not_found.xml",
        "views/testing_stage_views.xml",
        "views/testing_issue_views.xml",
        "views/testing_product_views.xml",
        "views/testing_menus.xml",
    ],
    "application": True,
    "installable": True,
}
