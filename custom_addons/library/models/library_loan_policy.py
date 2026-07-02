from odoo import models
from odoo.exceptions import ValidationError


class LibraryLoanPolicy(models.AbstractModel):
    _name = 'library.loan.policy'
    _description = 'Library Loan Policy'

    def _check_loan_dates(self, borrow_date, expected_return_date=None, return_date=None):
        if borrow_date and expected_return_date and expected_return_date < borrow_date:
            raise ValidationError(
                'Ngay tra du kien khong duoc nho hon ngay muon.'
            )

        if borrow_date and return_date and return_date < borrow_date:
            raise ValidationError(
                'Ngay tra thuc te khong duoc nho hon ngay muon.'
            )