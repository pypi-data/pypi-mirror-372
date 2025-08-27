import logging

from odoo.exceptions import UserError
from .base import BaseContractProcess

_logger = logging.getLogger(__name__)


class BAContractProcess(BaseContractProcess):
    _name = "ba.contract.process"
    _inherit = "base.contract.process"
    _register = True
    _description = """
        Broadband Contract creation
    """

    def _get_router_product_id(self, router_code):
        router_product = (
            self.env["product.product"]
            .sudo()
            .search(
                [
                    ("default_code", "=", router_code),
                ]
            )
        )
        if router_product:
            return router_product
        else:
            raise UserError("No router product with code %s" % router_code)

    def _create_router_lot_id(self, serial_number, product):
        return (
            self.env["stock.lot"]
            .sudo()
            .create(
                {
                    "product_id": product.id,
                    "name": serial_number,
                }
            )
        )

    def _get_project_xoln_id_by_code(self, project_code):
        xoln_project = self.env["xoln.project"].search([("code", "=", project_code)])
        if not xoln_project:
            raise UserError("Project with code %s not found" % (project_code,))
        return xoln_project.id
