from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create
from odoo.exceptions import ValidationError


class TestCRMLeadAddMultimediaLine(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.env.ref("somconnexio.res_partner_1_demo")
        self.filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")

    def test_create_line_with_existing_fiber_service(self):
        """
        Test the creation of a multimedia line in a CRM lead for a Filmin product.
        This test checks that a user with previous Filmin services activated
        cannot add another Filmin service through this wizard
        """

        self.assertTrue(self.partner_id.has_had_filmin_service)

        fiber_crm_lead = crm_lead_create(
            self.env, self.partner_id, "fiber", portability=False
        )

        self.assertFalse(fiber_crm_lead.has_multimedia_lead_lines)

        wizard_vals = {
            "product_id": self.filmin_product.id,
            "bank_id": self.partner_id.bank_ids.id,
        }
        wizard = (
            self.env["crm.lead.add.multimedia.line.wizard"]
            .with_context(active_id=fiber_crm_lead.id)
            .create(wizard_vals)
        )

        self.assertRaisesRegex(
            ValidationError,
            "A Filmin contract already exists for this partner: %s."
            % self.partner_id.id,
            wizard.button_create,
        )

    def test_create_line_with_no_existing_fiber_service(self):
        """
        Test the creation of a multimedia line in a CRM lead for a Filmin product.
        This test checks that a user without previous Filmin services activated
        can add another Filmin service through this wizard
        """
        partner_id = self.env.ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner_id.has_had_filmin_service)

        fiber_crm_lead = crm_lead_create(
            self.env, partner_id, "fiber", portability=False
        )

        self.assertFalse(fiber_crm_lead.has_multimedia_lead_lines)

        wizard_vals = {
            "product_id": self.filmin_product.id,
            "bank_id": partner_id.bank_ids.id,
        }
        wizard = (
            self.env["crm.lead.add.multimedia.line.wizard"]
            .with_context(active_id=fiber_crm_lead.id)
            .create(wizard_vals)
        )
        wizard.button_create()

        self.assertTrue(fiber_crm_lead.has_multimedia_lead_lines)
