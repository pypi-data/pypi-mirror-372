from odoo import models


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    def create_multimedia_contract(self):
        """
        Check that no previous filmin contracts exist for the lead partner,
        and create a new multimedia contract from the lead line.
        If the product is Filmin, set the service supplier to Filmin.
        """

        filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")
        if self.product_id == filmin_product:
            partner_id = self.lead_id.partner_id
            partner_id.check_filmin_service_allowed()

        return super().create_multimedia_contract()

    def _get_service_supplier(self):
        """
        Get the filmin service supplier contract.
        This overrides the unimplemented method in multimedia_somconnexio
        :return: Service supplier record
        """
        if self.product_id == self.env.ref("filmin_somconnexio.FilminSubscription"):
            return self.env.ref("filmin_somconnexio.service_supplier_filmin")
