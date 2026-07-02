from odoo import api, fields, models

class LibraryBook(models.Model):
    _name='library.book'
    _description = 'Library Book'

    name=fields.Char(string="Ten Sach", required=True)
    isbn=fields.Char(string='Ma ISBN')
    author=fields.Char(string='Tac gia')
    category_id=fields.Many2one('library.category',string="Danh muc")
    publisher_date=fields.Date(string='Ngay phat hanh')
    total_copies=fields.Integer(string='So ban sao', default=1)
    loan_ids=fields.One2many('library.loan','book_id',string='Phieu muon sach')
    borrowed_copies=fields.Integer(
        string='So luong sach muon',
        compute='_compute_borrowed_copies',
        store=True,
    )
    available_copies=fields.Integer(
        string='So luong sach con co lai',
        compute='_compute_available_copies',
        store=True,
    )
    state=fields.Selection(
        [
            ('available','Con sach'),
            ('unavailable','Het sach'),
        ],
        string='Trang thai',
        compute='_compute_state',
        store=True,
    )

    @api.depends('total_copies', 'borrowed_copies')
    def _compute_available_copies(self):
        #for book in self:
            #book.available_copies = book.total_copies - book.borrowed_copies

        self.available_copies = self.total_copies - self.borrowed_copies

    @api.depends('available_copies')
    def _compute_state(self):
        for book in self:
            if book.available_copies > 0:
                book.state = 'available'
            else:
                book.state = 'unavailable'

    @api.depends('loan_ids.state')
    def _compute_borrowed_copies(self):
        for book in self:
            book.borrowed_copies = len(book.loan_ids.filtered(
                lambda loan: loan.state == 'borrowed'
            ))

    _sql_constraints = [
        (
            'unique_isbn',
            'unique(isbn)',
            'Ma ISBN khong duoc trung!'
        ),
        (
            'check_total_copies_positive',
            'CHECK(total_copies > 0)',
            'Tong so ban sach phai lon hon 0!'
        )
    ]

    def action_open_borrow_wizard(self):
        self.ensure_one()

        action = self.env['ir.actions.actions']._for_xml_id(
            'library.library_borrow_wizard_action'
        )

        action['context'] = {
            'default_book_id': self.id,
        }

        return action
