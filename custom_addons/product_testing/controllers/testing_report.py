from odoo import http
from odoo.http import request


class TestingReportController(http.Controller):

    @http.route(
        "/testing/report/<int:product_id>",
        type="http",
        auth="public",
    )
    def testing_product_report(self, product_id):
        product = request.env["testing.product"].sudo().browse(product_id).exists()

        if not product:
            raise request.not_found()

        issues = request.env["testing.issue"].sudo().search([
            ("product_id", "=", product.id),
        ])

        return request.render(
            "product_testing.testing_product_report",
            {
                "product": product,
                "issues": issues,
            },
        )
