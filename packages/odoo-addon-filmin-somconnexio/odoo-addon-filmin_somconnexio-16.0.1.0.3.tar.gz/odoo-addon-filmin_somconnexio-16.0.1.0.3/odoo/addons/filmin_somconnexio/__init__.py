from . import models, listeners, wizards
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def _demo_stock_lots_move(cr, registry):
    """
    Post init hook to create a stock move for the demo data
    """

    env = api.Environment(cr, SUPERUSER_ID, {})

    is_dev = _is_this_dev(env)
    if not is_dev:
        _logger.info("❌ Skipping Filmin demo hook, not in development mode.")
        return

    product = env.ref("filmin_somconnexio.FilminSubscription")
    lots = [
        env.ref("filmin_somconnexio.stock_filmin_01"),
        env.ref("filmin_somconnexio.stock_filmin_02"),
        env.ref("filmin_somconnexio.stock_filmin_03"),
    ]

    # ---------------------
    # Move lots IN as stock
    # ---------------------

    move_in = env["stock.move"].create(
        {
            "name": "Bring serial Filmin products in stock",
            "location_id": env.ref("stock.stock_location_suppliers").id,
            "location_dest_id": env.ref("stock.stock_location_stock").id,
            "product_id": product.id,
            "product_uom": product.uom_id.id,
            "product_uom_qty": float(len(lots)),
        }
    )
    move_in._action_confirm()

    # Assing the 3 demo stock.lots with stock.move.lines
    move_in.move_line_ids.unlink()
    for lot in lots:
        env["stock.move.line"].create(
            {
                "move_id": move_in.id,
                "location_id": move_in.location_id.id,
                "location_dest_id": move_in.location_dest_id.id,
                "product_id": product.id,
                "product_uom_id": product.uom_id.id,
                "qty_done": 1.0,
                "lot_id": lot.id,
                "lot_name": lot.name,
            }
        )
    move_in._action_done()

    _logger.info("✅ Demo move from Filmin to stock correctly processed.")

    # ------------------------------
    # Move lot FLM0003 out from stock
    # -------------------------------

    move_out = env["stock.move"].create(
        {
            "name": "Send one serial Filmin product out",
            "location_id": env.ref("stock.stock_location_stock").id,
            "location_dest_id": env.ref("stock.stock_location_customers").id,
            "product_id": product.id,
            "product_uom": product.uom_id.id,
            "product_uom_qty": 1.0,
        }
    )
    move_out._action_confirm()
    move_out._action_assign()

    # Assing the FLM0003 demo stock.lots to stock.move.line (generated automatically)
    lot_used = lots[-1]
    move_out_line = move_out.move_line_ids[0]
    move_out_line.write(
        {
            "lot_id": lot_used.id,
            "lot_name": lot_used.name,
            "qty_done": 1.0,
        }
    )
    move_out._action_done()

    _logger.info("✅ Demo move out from stock correctly processed.")


def _is_this_dev(env):
    """
    Check if the current environment is in development mode.
    This is used to avoid running demo hooks in production environments.
    """
    demo_lot = env.ref("filmin_somconnexio.stock_filmin_01", raise_if_not_found=False)
    return bool(demo_lot and demo_lot.exists())
