from odoo import fields, models

class TestingStage(models.Model):
    _name = 'testing.stage'
    _description = 'Testing Stage'
    _order = 'sequence,id'


    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default = 10)
    fold = fields.Boolean(string="Folded in Kanban")

    _code_unique = models.Constraint(
        "unique(code)",
        "Stage code must be unique.",
    )


