from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_priority = fields.Selection(
        [
            ('normal', 'Binh thuong'),
            ('fast', 'Nhanh'),
            ('urgent', 'Hoa toc'),
        ],
        string = 'Muc do giao hang', default='normal',
    )

    requested_delivery_date = fields.Datetime(string='Ngay yeu cau giao')

    urgent_delivery_state = fields.Selection(
        [
            ('none', 'Khong can Duyet'),
            ('to_approve','Can Duyet'),
            ('approved', 'Da Duyet'),
            ('rejected', 'Da tu choi'),
        ],
        string = 'Trang thai', default="none",
    )


    def _requires_urgent_delivery_approval(self):
        self.ensure_one()
        return (
            self.delivery_priority == 'urgent'
            and self.urgent_delivery_state != 'approved'
        )

    def _requires_approval(self):
        self.ensure_one()
        return (
            super()._requires_approval()
            or self._requires_urgent_delivery_approval()
        )

    @api.depends(
        'order_line.discount',
        'order_line.display_type',
        'delivery_priority',
        'urgent_delivery_state',
    )
    def _compute_requires_approval(self):
        super()._compute_requires_approval()

    def action_open_urgent_delivery_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Duyet giao gap",
            "res_model": "urgent.delivery.approval.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_id": self.id,
            },
        }


    def action_confirm(self):
        for order in self:
            if order.delivery_priority == "urgent" and order.urgent_delivery_state == "rejected":
                raise UserError("Don giao gap da bi tu choi, khong the xac nhan.")

        urgent_orders_to_approve = self.filtered(
            lambda order: (
                order.state in {"draft", "sent", "to_approve"}
                and order._requires_urgent_delivery_approval()
            )
        )
        if urgent_orders_to_approve:
            urgent_orders_to_approve.write({
                "state": "to_approve",
                "urgent_delivery_state": "to_approve",
            })


        urgent_discount_orders_to_approve = urgent_orders_to_approve.filtered(
            lambda order: (
                order._requires_discount_approval()
                and not order.discount_approved
            )
        )
        if urgent_discount_orders_to_approve:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Approval Required'),
                    'message': _('Discount lớn hơn 10% và giao hỏa tốc cần được duyệt trước khi xác nhận.'),
                    'type': 'warning',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
                }
            }

        if urgent_orders_to_approve:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Urgent Delivery Approval Required'),
                    'message': _('Don giao hoa toc can duoc duyet truoc khi xac nhan.'),
                    'type': 'warning',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
                }
            }

        return super().action_confirm()

    def _confirmation_error_message(self):
        self.ensure_one()
        if (
            self.state == "to_approve"
            and not self._requires_urgent_delivery_approval()
            and not (
                self._requires_discount_approval()
                and not self.discount_approved
            )
        ):
            if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
            ):
                return _(
                    "Some order lines are missing a product, "
                    "you need to correct them before going further."
                )
            return False

        return super()._confirmation_error_message()
