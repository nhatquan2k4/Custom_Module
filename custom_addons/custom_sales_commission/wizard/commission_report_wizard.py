from datetime import datetime, time

from odoo import api, fields, models
from odoo.exceptions import UserError



class CommissionReportWizard(models.TransientModel):
    _name = "sales.commission.report.wizard"
    _description = "Sales Commission Report Wizard"

    name = fields.Char(
        string="Ten bao cao",
        default="Bao cao thuong",
    )

    date_from = fields.Date(string="Tu ngay", required=True)
    date_to = fields.Date(string="Den ngay", required=True)

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Nhan vien",
    )

    result_line_ids = fields.Many2many(
        "sales.commission.line",
        string="Ket qua bao cao",
    )

    result_count = fields.Integer(
        string="So dong",
        compute="_compute_result_totals",
    )

    sale_amount_total = fields.Monetary(
        string="Tong doanh so",
        compute="_compute_result_totals",
        currency_field="currency_id",
    )

    commission_amount_total = fields.Monetary(
        string="Tong tien thuong",
        compute="_compute_result_totals",
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Tien te",
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("result_line_ids", "result_line_ids.sale_amount", "result_line_ids.commission_amount")
    def _compute_result_totals(self):
        for wizard in self:
            wizard.result_count = len(wizard.result_line_ids)
            wizard.sale_amount_total = sum(wizard.result_line_ids.mapped("sale_amount"))
            wizard.commission_amount_total = sum(wizard.result_line_ids.mapped("commission_amount"))

    def action_view_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise UserError("Tu ngay phai nho hon hoac bang Den ngay.")

        date_from = datetime.combine(self.date_from, time.min)
        date_to = datetime.combine(self.date_to, time.max)

        domain = [
            ("order_date", ">=", fields.Datetime.to_string(date_from)),
            ("order_date", "<=", fields.Datetime.to_string(date_to)),
            ("commission_id.state", "=", "approved"),
        ]

        if self.employee_ids:
            domain.append(("employee_id", "in", self.employee_ids.ids))

        lines = self.env["sales.commission.line"].search(domain)
        self.result_line_ids = lines

        return {
            "type": "ir.actions.act_window",
            "res_model": "sales.commission.report.wizard",
            "res_id": self.id,
            "view_mode": "form",
        }
