from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('to_approve', 'Chờ duyệt'),
            ('sale',),
        ],
        ondelete={
            'to_approve': 'set default',
        }
    )

    requires_approval = fields.Boolean(
        string='Bắt buộc Duyệt',
        compute='_compute_requires_approval',
        store=True
    )

    discount_approved = fields.Boolean(
        string='Duyệt Discount',
        copy=False
    )

    approved_by = fields.Many2one(
        comodel_name='res.users',
        string='Duyệt bởi',
        readonly=True,
        copy=False
    )

    approved_date = fields.Datetime(
        string='Ngày Duyệt',
        readonly=True,
        copy=False
    )

    def _requires_discount_approval(self):
        self.ensure_one()
        return any(
            line.discount > 10
            for line in self.order_line
            if not line.display_type
        )

    def _requires_approval(self):
        self.ensure_one()
        return self._requires_discount_approval()

    @api.depends('order_line.discount', 'order_line.display_type')
    def _compute_requires_approval(self):
        for order in self:
            order.requires_approval = order._requires_approval()

    def action_confirm(self):
        for order in self:
            error_msg = order._confirmation_error_message()
            if error_msg:
                raise UserError(error_msg)

        orders_to_approve = self.filtered(
            lambda order: (
                    order.state in {'draft', 'sent'}
                    and order._requires_discount_approval()
                    and not order.discount_approved
            )
        )
        if orders_to_approve:
            orders_to_approve.write({'state': 'to_approve'})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Discount Approval Required'),
                    'message': _('Discount lớn hơn 10%. Cần Duyệt'),
                    'type': 'warning',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
                }
            }

        return super().action_confirm()

    def _confirmation_error_message(self):
        self.ensure_one()
        if self.state == 'to_approve' and self.discount_approved:
            if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
            ):
                return _(
                    'Some order lines are missing a product, '
                    'you need to correct them before going further.'
                )
            return False

        return super()._confirmation_error_message()

    def action_approve_discount(self):
        for order in self:
            if order.state != 'to_approve':
                raise ValidationError(
                    'Chỉ có Báo giá đang ở trạng thái Cần Duyệt mới phải Duyệt'
                )

            order.write({
                'discount_approved': True,
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })

        return self.action_confirm()
