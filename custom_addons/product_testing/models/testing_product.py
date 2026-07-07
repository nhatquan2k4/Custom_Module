from odoo import api, fields, models
from odoo.exceptions import UserError

class TestingProduct(models.Model):
    _name = "testing.product"
    _description = "Testing Product"

    def _default_stage_id(self):
        return self.env.ref(
            "product_testing.stage_analysis",
            raise_if_not_found=False,
        )

    name = fields.Char(string="Product", required = True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    stage_id = fields.Many2one(
        "testing.stage",
        default=lambda self: self._default_stage_id(),
        group_expand="_read_group_stage_ids",
        ondelete="restrict",
        required=True,
        copy=False,
    )

    kanban_state = fields.Selection(
        [
            ("normal", "Normal"),
            ('blocked', 'Blocked'),
            ("done", "Done"),
        ],
        default="normal",
        required=True,
    )
    color = fields.Integer(string="Color Index")
    responsible_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
    )
    tester_id = fields.Many2one("res.partner", string="Main Tester")
    planned_release_date = fields.Date()
    description = fields.Text()
    issue_ids = fields.One2many(
        "testing.issue",
        "product_id",
        string="Issues",
    )
    issue_count = fields.Integer(
        string="Issues",
        compute="_compute_issue_count",
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        stage_ids = stages.sudo()._search([], order=stages._order)
        return stages.browse(stage_ids)


    @api.depends("issue_ids")
    def _compute_issue_count(self):
        issue_data = self.env["testing.issue"]._read_group(
            [("product_id", "in", self.ids)],
            ["product_id"],
            ["__count"],
        )
        mapped_data = {product.id: count for product, count in issue_data}
        for product in self:
            product.issue_count = mapped_data.get(product.id, 0)

    def action_view_issues(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product_testing.action_testing_issue"
        )
        action["domain"] = [("product_id", "=", self.id)]
        action["context"] = {
            "default_product_id": self.id,
        }
        return action

    def action_mark_done(self):
        done_stage = self.env["testing.stage"].search(
            [("is_done", "=", True)],   
        )
        if not done_stage:
            raise UserError(self.env._("The completed stage has not been configured."))

        self.write({
            "stage_id": done_stage.id,
            "kanban_state": "done",
        })
        return True

    def write(self, vals):
        if vals.get("stage_id") and "kanban_state" not in vals:
            stage = self.env["testing.stage"].browse(vals["stage_id"])
            vals["kanban_state"] = "done" if stage.is_done else "normal"
        return super().write(vals)


    def action_open_report(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/testing/report/%s" % self.id,
            "target": "new",
        }
