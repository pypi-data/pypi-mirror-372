import logging

from odoo import models

_log = logging.getLogger(__name__)


class ServerActions(models.Model):
    """Add email option in server actions."""

    _name = "ir.actions.server"
    _description = "Server Action"
    _inherit = ["ir.actions.server"]

    def run_action_background_email(self, action, eval_context=None):
        active_id = self.env.context["active_id"]
        # Do not send mails for single Filmin line
        crm_lead = self.env["crm.lead"].browse(active_id)
        if crm_lead.has_single_filmin_line:
            return
        else:
            super(ServerActions, self).run_action_background_email(action, eval_context)
