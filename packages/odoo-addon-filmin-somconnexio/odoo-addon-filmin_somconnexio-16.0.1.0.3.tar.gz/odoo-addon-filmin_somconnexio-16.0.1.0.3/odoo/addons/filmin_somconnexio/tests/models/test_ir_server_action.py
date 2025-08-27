from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create
from mock import patch


class IrServerActionTest(SCTestCase):
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
        self.IrActionsServer = self.env["ir.actions.server"]
        self.action = object()

    @patch(
        "odoo.addons.somconnexio.models.ir_server_action.ServerActions.run_action_background_email"  # noqa: E501
    )
    def test_action_run_background_email_single_filmin_line(
        self, mock_run_action_background_email
    ):
        """Test that the run_action_background_email does not send an email
        if there is a single Filmin line."""
        self.assertTrue(self.lead.has_single_filmin_line)

        self.IrActionsServer.with_context(
            active_id=self.lead.id
        ).run_action_background_email(self.action)
        mock_run_action_background_email.assert_not_called()

    @patch(
        "odoo.addons.somconnexio.models.ir_server_action.ServerActions.run_action_background_email"  # noqa: E501
    )
    def test_action_run_background_email_fiber_line(
        self, mock_run_action_background_email
    ):
        """Test that the run_action_background_email sends an email
        if there is a fiber line."""
        self.assertFalse(self.fiber_lead.has_single_filmin_line)
        self.IrActionsServer.with_context(
            active_id=self.fiber_lead.id
        ).run_action_background_email(self.action)
        mock_run_action_background_email.assert_called_once_with(self.action, None)
