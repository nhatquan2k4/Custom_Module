from odoo import api, fields, models
from odoo.exceptions import ValidationError

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'

    name=fields.Char(string='Ten phieu muon', default='New')
    book_id=fields.Many2one('library.book', required = True, string ='Sach')
    member_id=fields.Many2one('library.member', required = True, string='Thanh vien')
    borrow_date=fields.Date(string='Ngay muon', default = fields.Date.today())
    expected_return_date=fields.Date(
        string='Ngay tra du kien',
        default=lambda self: fields.Date.add(fields.Date.today(), days=7),
    )
    return_date=fields.Date(string='Ngay tra thuc te')
    duration_days=fields.Integer(
        string='So ngay muon',
        compute='_compute_duration_days',
    )
    late_days=fields.Integer(
        string='So ngay tra qua han',
        compute='_compute_late_days',
    )
    late_fee=fields.Integer(
        string='Phi phat qua han',
        compute='_compute_late_fee',
        groups='group_library_manager'
    )
    state=fields.Selection([
        ('draft','Nhap'),
        ('borrowed','Dang muon'),
        ('returned','Da tra'),
        ('cancelled','Da huy'),
    ],
    string='Trang thai',
    default='draft',
    )
    note=fields.Text(string='Ghi chu')

    @api.constrains('borrow_date', 'expected_return_date', 'return_date')
    def _check_return_date(self):
        policy = self.env['library.loan.policy']

        for loan in self:
            policy._check_loan_dates(
                borrow_date=loan.borrow_date,
                expected_return_date=loan.expected_return_date,
                return_date=loan.return_date,
            )

    @api.depends('borrow_date', 'expected_return_date', 'return_date')
    def _compute_duration_days(self):
        for loan in self:
            end_date = loan.return_date or loan.expected_return_date
            if loan.borrow_date and end_date:
                loan.duration_days = (end_date - loan.borrow_date).days
            else:
                loan.duration_days = 0

    @api.depends('expected_return_date', 'return_date')
    def _compute_late_days(self):
        for loan in self:
            if loan.expected_return_date and loan.return_date:
                late_days = (loan.return_date - loan.expected_return_date).days
                loan.late_days = max(late_days, 0)
            else:
                loan.late_days = 0

    @api.depends('late_days')
    def _compute_late_fee(self):
        for loan in self:
            loan.late_fee = loan.late_days * 5000


    @api.constrains('member_id', 'state')
    def _check_max_borrowed_books(self):
        for loan in self:
            if not loan.member_id:
                continue

            borrowed_loans = loan.member_id.loan_ids.filtered(
                lambda l: l.state == 'borrowed'
            )

            if len(borrowed_loans) > 3:
                raise ValidationError(
                    'Mỗi thành viên không được mượn quá 3 quyển sách đang ở trạng thái Đang mượn.'
                )

    def action_confirm_borrow(self):
        for loan in self:
            loan.state = 'borrowed'

    def action_return_book(self):
        for loan in self:
            loan.state = 'returned'
            loan.return_date = fields.Date.today()
