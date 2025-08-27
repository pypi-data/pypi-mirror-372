from odoo import models, fields


class CRMLead(models.Model):
    _inherit = "crm.lead"

    has_single_filmin_line = fields.Boolean(
        string="Is only one Filmin line",
        help="Indicates if this lead has only one Filmin line.",
        compute="_compute_has_single_filmin_line",
        default=False,
    )

    def _compute_has_single_filmin_line(self):
        for lead in self:
            lead.has_single_filmin_line = len(
                lead.lead_line_ids
            ) == 1 and lead.lead_line_ids[0].product_id == self.env.ref(
                "filmin_somconnexio.FilminSubscription"
            )

    def action_send_email(self):
        """Override to ensure the email is not sent if there is a single Filmin line."""
        for lead in self:
            if lead.has_single_filmin_line:
                return False
            else:
                return super(CRMLead, lead).action_send_email()
