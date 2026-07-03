{
    "name": "Product Testing",
    "summary": "Manage product testing stages and tester issues",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/testing_stage_data.xml",
        "views/testing_stage_views.xml",
        "views/testing_issue_views.xml",
        "views/testing_product_views.xml",
        "views/testing_menus.xml",
    ],
    "application": True,
    "installable": True,
}
