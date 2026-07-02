from odoo import api, fields, models

class LibraryMember(models.Model):
    _name='library.member'
    _description = 'Library Member'

    name=fields.Char(string='Ten thanh vien', required=True)
    email=fields.Char(string='Email')
    phone=fields.Char(string='So dien thoai')
    join_date=fields.Date(string='Ngay dang ky', default = fields.Date.today())
    loan_ids=fields.One2many(
        'library.loan',
        'member_id',
        string='Phieu muon sach',
    )
    active_loan_count=fields.Integer(
        string='Tong so phieu muon sach',
        compute='_compute_active_loan_count',
    )
    active=fields.Boolean(string='Hoat dong', default=True)

    @api.depends('loan_ids.state')
    def _compute_active_loan_count(self):
        for member in self:
            member.active_loan_count = len(member.loan_ids.filtered(
                lambda loan: loan.state == 'borrowed'
            ))

    def action_open_borrow_wizard(self):
        self.ensure_one()

        action = self.env['ir.actions.actions']._for_xml_id(
            'library.library_borrow_wizard_action'
        )

        action['context'] = {
            'default_member_id': self.id,
        }

        return action