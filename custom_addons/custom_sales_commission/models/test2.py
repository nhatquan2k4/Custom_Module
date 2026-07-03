from odoo import models, fields


class Test2(models.Model):
    _name = "test.2"
    _description = "Test 2"

    name = fields.Char(required=True)
    test1_id = fields.Many2one(
        comodel_name="test.1",
        string="Test 1",
    )
    test1_m2m_ids = fields.Many2many(
        comodel_name="test.1",
        relation="test1_test2_rel",
        column1="test2_id",
        column2="test1_id",
        string="Test 1 Many2many",
    )

