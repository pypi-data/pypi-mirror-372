from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class TestCreateLeadFromPartner(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_1_demo")
        self.filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")
        self.wizard_params = {
            "opportunity": "test",
            "phone_contact": "888888888",
            "product_id": self.filmin_product.id,
            "product_categ_id": self.ref("multimedia_somconnexio.multimedia_service"),
            "bank_id": self.partner_id.bank_ids[0].id,
            "email_id": self.partner_id.id,
        }

    def test_create_lead_with_existing_fiber_service(self):
        """
        Test the manual creation of a multimedia lead for a Filmin product.
        This test checks that a user with previous Filmin services activated
        cannot create another Filmin service petition through this wizard
        """

        self.assertTrue(self.partner_id.has_had_filmin_service)

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner_id.id)
            .create(self.wizard_params)
        )

        self.assertRaisesRegex(
            ValidationError,
            "A Filmin contract already exists for this partner: %s."
            % self.partner_id.id,
            wizard.create_lead,
        )

    def test_create_lead_without_existing_fiber_service(self):
        """
        Test the manual creation of a multimedia lead for a Filmin product.
        This test checks that a user without previous Filmin services activated
        can create another Filmin service petition through this wizard
        """

        partner_id = self.env.ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner_id.has_had_filmin_service)

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=partner_id.id)
            .create(self.wizard_params)
        )

        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])

        self.assertTrue(crm_lead.has_multimedia_lead_lines)
