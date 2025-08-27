from odoo import models


class CRMLeadAddMultimediaLine(models.TransientModel):
    _inherit = "crm.lead.add.multimedia.line.wizard"

    def button_create(self):
        self.ensure_one()

        filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")

        if self.product_id == filmin_product:
            self.partner_id.check_filmin_service_allowed()

        return super().button_create()
