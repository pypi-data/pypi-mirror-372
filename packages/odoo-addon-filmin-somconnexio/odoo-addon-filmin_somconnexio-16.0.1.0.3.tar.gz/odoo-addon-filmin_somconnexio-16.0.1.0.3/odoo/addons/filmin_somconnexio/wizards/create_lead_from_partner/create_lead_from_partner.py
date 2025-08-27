from odoo import models


class CreateLeadFromPartner(models.TransientModel):
    _inherit = "partner.create.lead.wizard"

    def create_lead(self):
        self.ensure_one()
        filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")

        if self.product_id == filmin_product:
            self.partner_id.check_filmin_service_allowed()

        return super().create_lead()
