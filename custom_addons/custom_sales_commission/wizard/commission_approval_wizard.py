from odoo import fields, models
from odoo.exceptions import UserError


class CommissionApprovalWizard(models.TransientModel):
    _name = "sales.commission.approval.wizard"
    _description = "Sales Commission Approval Wizard"

    action = fields.Selection(
        [
            ("approve", "Phe duyet"),
            ("reject", "Tu choi"),
        ],
        string="Hanh dong",
        required=True,
        default="approve",
    )

    note = fields.Text(string="Ghi chu / Ly do")

    def action_confirm(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids", [])
        commissions = self.env["sales.commission"].browse(active_ids)

        if not commissions:
            raise UserError("Khong tim thay phieu thuong can xu ly.")
        if self.action == "reject" and not self.note:
            raise UserError("Vui long nhap ly do tu choi.")

        if self.action == "approve":
            commissions.action_approve(self.note)
        else:
            commissions.action_reject(self.note)

        return {"type": "ir.actions.act_window_close"}
