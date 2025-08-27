from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    is_filmin = fields.Boolean(
        string="Is FILMIN",
        compute="_compute_is_filmin",
        store=True,
    )

    @api.depends("service_supplier_id")
    def _compute_is_filmin(self):
        filmin_supplier = self.env.ref(
            "filmin_somconnexio.service_supplier_filmin", raise_if_not_found=False
        )
        if not filmin_supplier:
            return
        for record in self:
            record.is_filmin = record.service_supplier_id == filmin_supplier

    @api.depends("subscription_code")
    def _compute_name(self):
        super(Contract, self)._compute_name()
        for contract in self:
            if contract.is_filmin:
                contract.name = f"FILMIN - {contract.subscription_code}"

    @api.depends("service_technology_id")
    def _compute_contract_type(self):
        super(Contract, self)._compute_contract_type()
        for record in self:
            if record.is_filmin:
                record.service_contract_type = "filmin"

    def _get_subscription_tech(self):
        """overrides method that inform subscription_technology in _to_dict parent"""
        return (
            self.service_contract_type
            if self.is_filmin
            else super()._get_subscription_tech()
        )
