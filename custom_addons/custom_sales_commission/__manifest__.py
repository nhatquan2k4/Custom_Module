{
    "name": "Custom Sales Commission",
    "version": "1.0",
    "category": "Sales",
    "summary": "Sales commission approval and reporting",
    "depends": [
        "sale_stock",
        "sale_crm",
        "hr",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/commission_approval_wizard_views.xml",
        "wizard/commission_report_wizard_views.xml",
        "views/sales_commission_views.xml",
    ],
    "installable": True,
    "application": True,

}
