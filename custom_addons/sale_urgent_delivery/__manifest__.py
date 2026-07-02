{
    "name": "Sale Urgent Delivery",
    "depends": ["sale_discount_approval"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_urgent_delivery.xml",
        "wizard/urgent_delivery_approval_wizard_views.xml",
    ],
    "application": True,
    "installable": True,
}