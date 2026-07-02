from odoo import api,models, fields

class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Library Category'

    name = fields.Char(string='Ten danh muc', required=True)
    description = fields.Text(string='Mo ta Danh muc')
    book_ids = fields.One2many('library.book', 'category_id', string='Danh sach Sach')
    book_count = fields.Integer(
        string='Book Count',
        compute='_compute_book_count',
    )

    _sql_constraints = [
        (
            "unique_category_name",
            "unique(name)",
            "Ten Danh muc khong duoc trung nhau"
        )
    ]

    @api.depends('book_ids')
    def _compute_book_count(self):
        for category in self:
            category.book_count = len(category.book_ids)