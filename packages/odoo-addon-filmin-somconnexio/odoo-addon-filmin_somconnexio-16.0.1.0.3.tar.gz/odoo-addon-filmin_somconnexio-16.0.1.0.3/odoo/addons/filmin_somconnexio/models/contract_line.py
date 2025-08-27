from odoo import models, fields, api


class ContractLine(models.Model):
    _inherit = "contract.line"

    lot_id = fields.Many2one("stock.lot", string="Serial Number")

    @api.model
    def create(self, vals):
        """
        Override the create method to handle the creation of a contract line
        and automatically assign a serial number if the product is tracked by
        serial number.
        Also, create a stock move for the internal consumption of the product.
        """
        res = super().create(vals)

        if res.lot_id:
            return res

        product = res.product_id
        if (
            product
            and product.detailed_type == "product"
            and product.tracking == "serial"
        ):
            lot = self._pick_lot_from_stock(res, product)
            self._assign_lot_to_contract(res, lot)

        return res

    def _assign_lot_to_contract(self, res, lot):
        """
        Assign the lot to the contract line and
        the lot name as the contract's subscription code.
        """
        res.lot_id = lot
        res.contract_id.subscription_code = lot.name

    def _pick_lot_from_stock(self, res, product):
        """
        Create a stock picking to move a unit out of stock
        """
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "origin": f"Pick out {product.showed_name} for contract {res.contract_id.id}",  # noqa: E501
            }
        )

        move = self.env["stock.move"].create(
            {
                "name": f"Move out {product.showed_name} for contract {res.contract_id.id}",  # noqa: E501
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_qty": 1.0,
                "product_uom": product.uom_id.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        move._action_confirm()
        move._action_assign()

        # One move line generated per move with serial product
        move_line = move.move_line_ids[0]
        move_line.write({"qty_done": 1.0})

        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()

        return move_line.lot_id
