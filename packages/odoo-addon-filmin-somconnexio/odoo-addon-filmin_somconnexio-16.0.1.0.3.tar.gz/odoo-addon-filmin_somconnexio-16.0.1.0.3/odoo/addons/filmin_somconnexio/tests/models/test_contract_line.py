from datetime import date
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from ..helper_service import contract_filmin_create_data


class TestContractLine(SCTestCase):
    def setUp(self):
        super().setUp()
        self.ContractLine = self.env["contract.line"]
        self.Quant = self.env["stock.quant"]
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.partner = self.env.ref("somconnexio.res_partner_company_demo")
        self.serial_product = self.env.ref("filmin_somconnexio.FilminSubscription")

        self.new_contract = self.env["contract.contract"].create(
            contract_filmin_create_data(self.env, self.partner)
        )

    def test_contract_line_creation_with_serial_product(self):
        """
        Test that if a contract line is created with a serial tracking product
        a stock lot is picked out from supply and assigned to the contract line
        and the contract's subscription code is set to the lot name.
        """
        self.assertEqual(self.serial_product.tracking, "serial")
        self.assertEqual(self.serial_product.detailed_type, "product")

        stock_quant_before = self.Quant.search(
            [
                ("product_id", "=", self.serial_product.id),
                ("location_id", "=", self.stock_location.id),
                ("quantity", "=", 1),
            ]
        )

        self.assertTrue(stock_quant_before)

        # create a new contract line with serial tracked product
        line = self.ContractLine.create(
            {
                "name": "Test Line",
                "contract_id": self.new_contract.id,
                "product_id": self.serial_product.id,
                "date_start": date.today(),
            }
        )

        stock_quant_after = self.Quant.search(
            [
                ("product_id", "=", self.serial_product.id),
                ("location_id", "=", self.stock_location.id),
                ("quantity", "=", 1),
            ]
        )

        lot_used = (stock_quant_before - stock_quant_after).lot_id
        self.assertTrue(lot_used)
        self.assertTrue(len(lot_used) == 1)
        self.assertEqual(line.lot_id, lot_used)
        self.assertEqual(line.contract_id.subscription_code, lot_used.name)

        move_out = self.env["stock.move"].search(
            [
                (
                    "name",
                    "=",
                    f"Move out {self.serial_product.showed_name} for contract {line.contract_id.id}",  # noqa: E501
                ),
                ("state", "=", "done"),
            ],
            limit=1,
        )

        self.assertTrue(move_out)
        self.assertEqual(move_out.product_id, self.serial_product)
        self.assertEqual(move_out.product_uom_qty, 1.0)
        self.assertEqual(move_out.location_id, self.stock_location)
        self.assertEqual(
            move_out.location_dest_id, self.env.ref("stock.stock_location_customers")
        )
        self.assertEqual(
            move_out.picking_type_id, self.env.ref("stock.picking_type_out")
        )
        self.assertEqual(move_out.move_line_ids[0].lot_id, lot_used)
        self.assertEqual(move_out.move_line_ids[0].qty_done, 1.0)
        self.assertTrue(move_out.picking_id)
        self.assertEqual(move_out.picking_id.state, "done")

    def test_non_serial_product_does_not_assign_lot(self):
        """
        Test that if a contract line is created with a non serial tracking product
        no stock lot is picked out from supply and none is assigned to the contract line
        """
        non_serial_product = self.serial_product.copy({"tracking": "none"})
        line = self.ContractLine.create(
            {
                "name": "Non-serial Line",
                "contract_id": self.new_contract.id,
                "product_id": non_serial_product.id,
                "date_start": date.today(),
            }
        )

        move_out = self.env["stock.move"].search(
            [
                (
                    "name",
                    "=",
                    f"Move out {non_serial_product.showed_name} for contract {line.contract_id.id}",  # noqa: E501
                ),
                ("state", "=", "done"),
            ],
            limit=1,
        )
        self.assertFalse(move_out)
        self.assertFalse(line.lot_id)
        self.assertFalse(line.contract_id.subscription_code)
