from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    has_had_filmin_service = fields.Boolean(
        string="Has had Filmin service",
        compute="_compute_has_had_filmin_service",
        defaults=False,
    )

    def _compute_has_had_filmin_service(self):
        """
        Compute if the partner has had a Filmin contract.
        This is used to determine if the partner can add a new Filmin line.
        """
        self.env.ref("filmin_somconnexio.FilminSubscription")
        multimedia_technology = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        )

        for partner in self:
            previous_partner_filmin_contracts = self.env["contract.contract"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("is_filmin", "=", True),
                    (
                        "service_technology_id",
                        "=",
                        multimedia_technology.id,
                    ),
                ]
            )
            partner.has_had_filmin_service = bool(previous_partner_filmin_contracts)

    def check_filmin_service_allowed(self):
        self.ensure_one()
        self.env.ref("filmin_somconnexio.FilminSubscription")
        if self.has_had_filmin_service:
            raise ValidationError(
                _("A Filmin contract already exists for this partner: %s.") % self.id
            )
