from odoo.addons.component.core import Component


class CrmLeadListener(Component):
    _name = "filmin.crm.lead.listener"
    _inherit = "multimedia.crm.lead.listener"

    def on_record_create(self, record, fields=None):
        """
        This method is triggered when a CRM lead record is created.
        It checks if the lead has just one lead line with filmin supplier.
        If so, it automatically validates the lead and sets it to the 'won' stage.
        """
        if record.has_single_filmin_line:
            record.action_set_remesa()
            record.action_set_won()
