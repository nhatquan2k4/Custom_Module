from odoo import api, fields, models
from odoo.exceptions import ValidationError

class TestingStage(models.Model):
    _name = 'testing.stage'
    _description = 'Testing Stage'
    _order = 'sequence,id'


    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default = 10)
    fold = fields.Boolean(string="Folded in Kanban")
    is_done = fields.Boolean(string="Is Done Stage?")

    @api.onchange("is_done")
    def _onchange_is_done(self):
        return {
            "warning": {
                "title": self.env._("Do you really want to update this stage?"),
                "message": self.env._(
                    "Changing the value of 'Is Done Stage?' will update the "
                    "Kanban state of products currently in this stage on saving."
                )
            }
        }

    def write(self, vals):
        res = super().write(vals)
        if "is_done" in vals:
            products = self.env["testing.product"].search([("stage_id", "in", self.ids)])
            if vals["is_done"]:
                products.write({"kanban_state": "done"})
            else:
                products.filtered(lambda product: product.kanban_state == "done").write({
                    "kanban_state": "normal",
                })
        return res

    @api.constrains("is_done")
    def _check_single_done_stage(self):
        if any(stage.is_done for stage in self):
            done_stages = self.search([("is_done", "=", True)])
            if len(done_stages) > 1:
                raise ValidationError(self.env._("Only one stage can be marked as done."))
