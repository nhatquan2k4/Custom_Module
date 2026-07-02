from odoo import fields, models


class LibraryBorrowWizard(models.TransientModel):
    _name = 'library.borrow.wizard'
    _description = 'Borrow Book Wizard'

    book_id = fields.Many2one(
        'library.book',
        string='Sach',
        required=True,
    )
    member_id = fields.Many2one(
        'library.member',
        string='Thanh vien',
        required=True,
    )
    borrow_date = fields.Date(
        string='Ngay muon',
        default=fields.Date.today,
    )
    expected_return_date = fields.Date(
        string='Ngay tra du kien',
        default=lambda self: fields.Date.add(fields.Date.today(), days=7),
    )
    note = fields.Text(string='Ghi chu')

    def action_confirm(self):
        self.ensure_one()

        loan = self.env['library.loan'].create({
            'book_id': self.book_id.id,
            'member_id': self.member_id.id,
            'borrow_date': self.borrow_date,
            'expected_return_date': self.expected_return_date,
            'note': self.note,
        })

        loan.action_confirm_borrow()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Loan',
            'res_model': 'library.loan',
            'res_id': loan.id,
            'view_mode': 'form',
            'target': 'current',
        }