from datetime import datetime, time

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class SalesCommission(models.Model):
    _name = "sales.commission"
    _description = "Sales Commission"
    _inherit = ["approval.audit.mixin"]

    name = fields.Char(string="Ma Phieu Thuong", required=True, default="New", copy=False)

    employee_id = fields.Many2one(
        "hr.employee",
        string="Nhan vien duoc tinh thuong",
        required=True,
    )

    salesperson_user_id = fields.Many2one(
        "res.users",
        string="Tài khoản Sales",
        related="employee_id.user_id",
        store=True,
        readonly=True,
    )

    period_from = fields.Date(string="Ngay bat dau tinh thuong", required=True)
    period_to = fields.Date(string="Ngay ket thuc tinh thuong", required=True)

    line_ids = fields.One2many(
        "sales.commission.line",
        "commission_id",
        string="Chi tiet Phieu tinh thuong",
    )

    sale_amount_total = fields.Monetary(
        string="Tong doanh so",
        compute="_compute_totals",
        store=True,
    )
    commission_amount_total = fields.Monetary(
        string="Tong tien thuong",
        compute="_compute_totals",
        store=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Tien te",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Cong ty",
        default=lambda self: self.env.company,
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Nhap"),
            ("to_approve", "Cho Duyet"),
            ("approved", "Da duyet"),
            ("rejected", "Tu choi"),
        ],
        string="Trang thai",
        default="draft",
        required=True,
    )

    _sql_constraints = [
        (
            "unique_employee_period_company",
            "unique(employee_id, period_from, period_to, company_id)",
            "Da ton tai phieu thuong cho nhan vien nay trong ky nay.",
        )
    ]

    @api.constrains("period_from", "period_to")
    def _check_period_dates(self):
        for record in self:
            if record.period_from and record.period_to and record.period_from > record.period_to:
                raise ValidationError("Ngay bat dau phai nho hon hoac bang ngay ket thuc.")

    @api.depends("line_ids.sale_amount", "line_ids.commission_amount")
    def _compute_totals(self):
        for commission in self:
            commission.sale_amount_total = sum(commission.line_ids.mapped("sale_amount"))
            commission.commission_amount_total = sum(commission.line_ids.mapped("commission_amount"))

    def _get_commission_rate(self, order):
        return 5.0

    def action_generate_lines(self):
        SaleOrder = self.env["sale.order"]
        CommissionLine = self.env["sales.commission.line"]  
        for commission in self:
            if commission.state == "approved":
                raise UserError("Khong the tinh lai phieu thuong da duyet.")
            if not commission.salesperson_user_id:
                raise UserError("Nhan vien duoc tinh thuong chua gan tai khoan nguoi dung.")
            if not commission.period_from or not commission.period_to:
                raise UserError("Vui long nhap day du ky tinh thuong.")

            existing_order_ids = CommissionLine.search([
                ("commission_id", "!=", commission.id),
                ("sale_order_id", "!=", False),
            ]).mapped("sale_order_id").ids

            date_from = datetime.combine(commission.period_from, time.min)
            date_to = datetime.combine(commission.period_to, time.max)

            domain = [
                ("state", "in", ("sale", "done")),
                ("delivery_status", "=", "full"),
                ("user_id", "=", commission.salesperson_user_id.id),
                ("company_id", "=", commission.company_id.id),
                ("date_order", ">=", fields.Datetime.to_string(date_from)),
                ("date_order", "<=", fields.Datetime.to_string(date_to)),
            ]
            if existing_order_ids:
                domain.append(("id", "not in", existing_order_ids))

            orders = SaleOrder.search(domain)
            commission.line_ids.unlink()

            line_values = []
            for order in orders:
                commission_rate = commission._get_commission_rate(order)
                line_values.append({
                    "commission_id": commission.id,
                    "sale_order_id": order.id,
                    "order_date": order.date_order,
                    "delivery_date": order.effective_date,
                    "sale_amount": order.amount_untaxed,
                    "commission_rate": commission_rate,
                    "delivery_status_snapshot": order.delivery_status,
                })
            if line_values:
                CommissionLine.create(line_values)

        return True

    def action_open_approval_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Duyet phieu thuong",
            "res_model": "sales.commission.approval.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "sales.commission",
                "active_ids": self.ids,
            },
        }

    def action_submit(self):
        for commission in self:
            if commission.state != "draft":
                raise UserError("Chi co phieu o trang thai Nhap moi duoc gui duyet.")
            if not commission.line_ids:
                raise UserError("Phieu thuong phai co it nhat mot dong truoc khi gui duyet.")
            commission.state = "to_approve"
        return True

    def action_approve(self, note=False):
        for commission in self:
            if commission.state != "to_approve":
                raise UserError("Chi co phieu o trang thai Cho Duyet moi duoc phe duyet.")
            commission.write({
                "state": "approved",
                "approved_by": self.env.user.id,
                "approved_date": fields.Datetime.now(),
                "approval_note": note,
            })
        return True

    def action_reject(self, reason):
        if not reason:
            raise UserError("Vui long nhap ly do tu choi.")
        for commission in self:
            if commission.state != "to_approve":
                raise UserError("Chi co phieu o trang thai Cho Duyet moi duoc tu choi.")
            commission.write({
                "state": "rejected",
                "rejected_by": self.env.user.id,
                "rejected_date": fields.Datetime.now(),
                "rejection_reason": reason,
            })
        return True
