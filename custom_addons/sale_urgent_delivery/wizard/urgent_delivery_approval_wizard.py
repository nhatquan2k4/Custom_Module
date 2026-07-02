from odoo import models, fields
from odoo.exceptions import UserError


class UrgentDeliveryApprovalWizard(models.TransientModel):
    _name = "urgent.delivery.approval.wizard"
    _description = "Urgent Delivery Approval Wizard"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get("default_sale_order_id"),
    )

    note = fields.Text(string="Ghi chu")

    def action_approve(self):
        self.ensure_one()

        if not self.sale_order_id:
            raise UserError("Khong tim thay Sale Order can duyet.")

        self.sale_order_id.write({
            "urgent_delivery_state": "approved",
        })

        action = self.sale_order_id.action_confirm()
        if isinstance(action, dict):
            return action

        return {"type": "ir.actions.act_window_close"}

    def action_reject(self):
        self.ensure_one()

        if not self.sale_order_id:
            raise UserError("Khong tim thay Sale Order can tu choi.")

        self.sale_order_id.write({
            "urgent_delivery_state": "rejected",
        })

        return {"type": "ir.actions.act_window_close"}
