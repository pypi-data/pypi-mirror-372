from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create
from odoo.exceptions import ValidationError


class CRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.filmin_product = self.env.ref("filmin_somconnexio.FilminSubscription")

    def test_create_filmin_contract_with_partner_having_one(self):
        """
        Test that from a filmin crm_lead_line with a partner that does have
        had previous filmin contracts before, no contract can be created,
        raising a ValidationError.
        """
        existing_filmin_contract = self.env.ref("filmin_somconnexio.contract_filmin")
        mm_lead = crm_lead_create(
            self.env, existing_filmin_contract.partner_id, "multimedia"
        )
        mm_crm_lead_line = mm_lead.lead_line_ids[0]
        mm_crm_lead_line.product_id = self.filmin_product

        self.assertRaisesRegex(
            ValidationError,
            "A Filmin contract already exists for this partner: %s."
            % existing_filmin_contract.partner_id.id,
            mm_crm_lead_line.create_multimedia_contract,
        )

    def test_create_filmin_contract_with_partner_first_one(self):
        """
        Test that from a filmin crm_lead_line a contract with the filmin
        service supplier can be created with a partner that does not have
        a filmin contract yet,
        """
        previous_filmin_contracts = self.env["contract.contract"].search(
            [
                ("partner_id", "=", self.partner_id.id),
                (
                    "service_technology_id",
                    "=",
                    self.env.ref(
                        "multimedia_somconnexio.service_technology_multimedia"
                    ).id,
                ),
                (
                    "service_supplier_id",
                    "=",
                    self.env.ref("filmin_somconnexio.service_supplier_filmin").id,
                ),
            ]
        )
        self.assertFalse(previous_filmin_contracts)

        # Create a CRM lead line for Filmin
        mm_lead = crm_lead_create(self.env, self.partner_id, "multimedia")
        mm_crm_lead_line = mm_lead.lead_line_ids[0]
        mm_crm_lead_line.product_id = self.filmin_product

        mm_contract = mm_crm_lead_line.create_multimedia_contract()

        self.assertTrue(mm_contract.id)
        self.assertEqual(
            mm_contract.service_supplier_id,
            self.env.ref("filmin_somconnexio.service_supplier_filmin"),
        )
        self.assertEqual(
            mm_contract.service_technology_id,
            self.env.ref("multimedia_somconnexio.service_technology_multimedia"),
        )
        self.assertEqual(mm_contract.partner_id, self.partner_id)
