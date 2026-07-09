from odoo import fields, models


class TestingIssue(models.Model):
    _name = "testing.issue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Testing Issue"
    _order = "priority desc, reported_date desc, id desc"

    name = fields.Char(string="Issue", required=True, tracking=True)
    product_id = fields.Many2one(
        "testing.product",
        string="Testing Product",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    tester_id = fields.Many2one("res.partner", tracking=True)
    reported_date = fields.Date(
        default=fields.Date.context_today,
        tracking=True,
    )
    priority = fields.Selection(
        [
            ("0", "Low"),
            ("1", "Normal"),
            ("2", "High"),
            ("3", "Critical"),
        ],
        default="1",
        required=True,
        tracking=True,
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
        tracking=True,
    )
    description = fields.Text()
    resolution = fields.Text()
