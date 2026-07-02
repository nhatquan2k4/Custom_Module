from odoo import fields, models


class ApprovalAuditMixin(models.AbstractModel):
    _name = "approval.audit.mixin"
    _description = "Approval Audit Mixin"

    approved_by = fields.Many2one(
        "res.users",
        string="Approved By",
        readonly=True,
        copy=False,
    )

    approved_date = fields.Datetime(
        string="Approved Date",
        readonly=True,
        copy=False,
    )

    approval_note = fields.Text(
        string="Approval Note",
        readonly=True,
        copy=False,
    )

    rejected_by = fields.Many2one(
        "res.users",
        string="Rejected By",
        readonly=True,
        copy=False,
    )

    rejected_date = fields.Datetime(
        string="Rejected Date",
        readonly=True,
        copy=False,
    )

    rejection_reason = fields.Text(
        string="Rejection Reason",
        readonly=True,
        copy=False,
    )