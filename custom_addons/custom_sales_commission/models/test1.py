from odoo import models, fields

class Test1(models.Model):
    _name = "test.1"
    _description = "Test 1"

    name = fields.Char(required=True)
    test2_ids = fields.One2many(
        comodel_name="test.2",
        inverse_name="test1_id",
        string="Test 2 Records",
    )
    test2_m2m_ids = fields.Many2many(
        comodel_name="test.2",
        relation="test1_test2_rel",
        column1="test1_id",
        column2="test2_id",
        string="Test 2 Many2many",
    )

    def action_test_command_create(self):
        self.ensure_one()

        self.write({
            "test2_ids": [
                (0, 0, {"name": "Create 1"}),
            ]
        })

        self.write({
            "test2_ids": [
                fields.Command.create({"name": "Create 2"}),
            ]
        })

        return {"type": "ir.actions.client", "tag": "reload"}

    def action_test_command_update(self):
        self.ensure_one()

        first_line = self.test2_ids[0]
        second_line = self.test2_ids[1]

        self.write({
            "test2_ids": [
                (1, first_line.id, {"name": "Updated Option1"}),
            ]
        })

        self.write({
            "test2_ids": [
                fields.Command.update(second_line.id, {"name": "Updated Option2"}),
            ]
        })

        return {"type": "ir.actions.client", "tag": "reload"}

    def action_test_command_link_and_unlink(self):
        self.ensure_one()

        first_record = self.env["test.2"].create({"name": "Unlink Option1"})
        second_record = self.env["test.2"].create({"name": "Unlink Option2"})

        self.write({
            "test2_m2m_ids": [
                fields.Command.link(first_record.id),
            ]
        })

        self.write({
            "test2_m2m_ids": [
                (4, second_record.id, 0),
            ]
        })

        self.write({
            "test2_m2m_ids": [
                (3, first_record.id, 0),
            ]
        })
        #
        # self.write({
        #     "test2_m2m_ids": [
        #         fields.Command.unlink(second_record.id),
        #     ]
        # })

        return {"type": "ir.actions.client", "tag": "reload"}



    def action_test_command_clear(self):
        self.ensure_one()

        self.write({
            "test2_m2m_ids": [
                (5, 0, 0),
            ]
        })

        self.write({
            "test2_m2m_ids": [
                fields.Command.clear(),
            ]
        })

        return {"type": "ir.actions.client", "tag": "reload"}

    def action_test_command_set(self):
        self.ensure_one()

        first_record = self.env["test.2"].create({"name": "Set Option1"})
        second_record = self.env["test.2"].create({"name": "Set Option2"})

        self.write({
            "test2_m2m_ids": [
                (6, 0, [first_record.id]),
            ]
        })

        self.write({
            "test2_m2m_ids": [
                fields.Command.set([second_record.id]),
            ]
        })

        return {"type": "ir.actions.client", "tag": "reload"}
