from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create
from mock import patch


class CRMLeadTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")
        self.lead = crm_lead_create(
            self.env,
            self.partner_id,
            "multimedia",
        )
        self.lead.lead_line_ids[0].product_id = self.filmin_product
        self.fiber_lead = crm_lead_create(
            self.env,
            self.partner_id,
            "fiber",
        )

    def test_crm_lead_has_single_filmin_line(self):
        """Test that a CRM lead with a single Filmin line is correctly identified."""

        self.assertTrue(len(self.lead.lead_line_ids) == 1)
        self.assertEqual(self.lead.lead_line_ids[0].product_id, self.filmin_product)
        self.lead._compute_has_single_filmin_line()
        self.assertTrue(self.lead.has_single_filmin_line)

    def test_crm_lead_has_not_single_filmin_line(self):
        """Test that a CRM lead mixed with Filmin is not identified
        as having a single Filmin line."""
        self.lead.lead_line_ids |= self.fiber_lead.lead_line_ids[0]

        self.assertTrue(len(self.lead.lead_line_ids) == 2)
        self.lead._compute_has_single_filmin_line()
        self.assertEqual(self.lead.lead_line_ids[0].product_id, self.filmin_product)
        self.assertNotEqual(self.lead.lead_line_ids[1].product_id, self.filmin_product)
        self.assertFalse(self.lead.has_single_filmin_line)

    @patch("odoo.addons.somconnexio.models.crm_lead.CrmLead.action_send_email")
    def test_action_send_mail_single_filmin_line(self, mock_action_send_email):
        """Test that the action_send_email does not send an email
        if there is a single Filmin line."""
        self.assertTrue(self.lead.has_single_filmin_line)
        self.lead.action_send_email()
        mock_action_send_email.assert_not_called()

    @patch("odoo.addons.somconnexio.models.crm_lead.CrmLead.action_send_email")
    def test_action_send_mail_fiber_line(self, mock_action_send_email):
        """Test that the action_send_email sends an email
        if there is a fiber line."""
        self.assertFalse(self.fiber_lead.has_single_filmin_line)
        self.fiber_lead.action_send_email()
        mock_action_send_email.assert_called_once()
