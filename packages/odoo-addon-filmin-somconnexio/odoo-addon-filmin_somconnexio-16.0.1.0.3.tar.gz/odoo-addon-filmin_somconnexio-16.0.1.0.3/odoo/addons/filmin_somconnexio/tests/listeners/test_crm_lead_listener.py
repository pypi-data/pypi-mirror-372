from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase
from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create


class TestCRMLeadListener(SCComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCRMLeadListener, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=False,
            )
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")
        self.crm_lead_line_filmin_vals = {
            "name": "Filmin Lead Line",
            "iban": self.partner_id.bank_ids[0].sanitized_acc_number,
            "product_id": self.filmin_product.id,
        }
        self.crm_lead_filmin_vals = {
            "name": "Test Lead",
            "partner_id": self.partner_id.id,
            "phone": self.partner_id.phone,
            "email_from": self.partner_id.email,
            "stage_id": self.env.ref("crm.stage_lead1").id,
            "lead_line_ids": [
                (
                    0,
                    0,
                    self.crm_lead_line_filmin_vals,
                )
            ],
        }

    def test_crm_lead_lead_single_filmin_validated_at_creation(self):
        """
        Test that a CRM lead with a single Filmin line is not validated
        at creation.
        """
        self.assertEqual(
            self.crm_lead_filmin_vals["stage_id"],
            self.env.ref("crm.stage_lead1").id,  # Draft
        )
        filmin_lead = self.env["crm.lead"].create(self.crm_lead_filmin_vals)
        self.assertTrue(
            filmin_lead.has_single_filmin_line,
        )
        self.assertEqual(
            filmin_lead.stage_id,
            self.env.ref("crm.stage_lead4"),  # Won
        )

    def test_crm_lead_lead_not_single_filmin_not_validated_at_creation(self):
        """
        Test that a CRM lead with False has_single_filmin_line is not validated
        at creation.
        """
        fiber_lead = crm_lead_create(
            self.env,
            self.partner_id,
            "fiber",
        )
        self.assertFalse(
            fiber_lead.has_single_filmin_line,
        )
        self.assertEqual(
            fiber_lead.stage_id,
            self.env.ref("crm.stage_lead1"),  # Draft
        )
