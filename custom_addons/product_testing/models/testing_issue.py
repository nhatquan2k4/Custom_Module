from odoo import fields, models


class TestingIssue(models.Model):
    _name = "testing.issue"
    _description = "Testing Issue"
    _order = "priority desc, reported_date desc, id desc"

    name = fields.Char(string="Issue", required=True)
    product_id = fields.Many2one(
        "testing.product",
        string="Testing Product",
        required=True,
        ondelete="cascade",
    )
    tester_id = fields.Many2one("res.partner", string="Tester")
    reported_date = fields.Date(
        string="Reported Date",
        default=fields.Date.context_today,
    )
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Critical"),
        ],
        string="Priority",
        default="1",
        required=True,
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("confirmed", "Confirmed"),
            ("fixed", "Fixed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="new",
        required=True,
    )
    description = fields.Text(string="Description")
    resolution = fields.Text(string="Resolution")
