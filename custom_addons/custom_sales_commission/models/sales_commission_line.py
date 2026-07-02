from odoo import models, fields, api

class SalesCommissionLine(models.Model):
    _name = "sales.commission.line"
    _description = "Sales Commission Line"

    commission_id = fields.Many2one(
        "sales.commission",
        string="Phieu thuong",
        required = True,
        ondelete = "cascade",
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Don hang duoc tinh thuong",
        required = True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Nhan vien duoc tinh thuong",
        related="commission_id.employee_id",
        store=True,
        readonly=True,
    )
    salesperson_user_id = fields.Many2one(
        "res.users",
        string="Tài khoản Sales",
        related="sale_order_id.user_id",
        readonly=True,
        store=True,
    )
    order_date = fields.Datetime(string="Ngay dat hang")
    delivery_date = fields.Datetime(string="Ngay giao hang")
    sale_amount = fields.Monetary(
        string = 'Doanh so hop le'
    )
    commission_rate = fields.Float(
        string = 'Ty le thuong'
    )
    commission_amount = fields.Monetary(
        string="Tien thuong",
        compute="_compute_commission_amount",
        store=True,
    )

    delivery_status_snapshot = fields.Selection(
        [
            ("pending", "Chua giao"),
            ("started", "Bat dau giao"),
            ("partial", "Giao mot phan"),
            ("full", "Da giao du"),
        ],
        string="Trang thai giao hang",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Tien te",
        related="commission_id.currency_id",
        store=True,
        readonly=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Cong ty",
        related="commission_id.company_id",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "unique_sale_order_commission",
            "unique(sale_order_id)",
            "Don hang nay da duoc tinh thuong.",
        )
    ]

    @api.depends('sale_amount', 'commission_rate')
    def _compute_commission_amount(self):
        for line in self:
            line.commission_amount = line.sale_amount * line.commission_rate / 100