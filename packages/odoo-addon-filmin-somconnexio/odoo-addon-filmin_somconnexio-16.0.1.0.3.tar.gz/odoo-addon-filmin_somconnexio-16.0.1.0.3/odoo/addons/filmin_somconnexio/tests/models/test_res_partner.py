from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class ResPartnerTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_1_demo")

    def test_has_had_filmin_service(self):
        """Test that a partner with a Filmin contract has the
        has_had_filmin_service field set to True."""

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
                    "is_filmin",
                    "=",
                    True,
                ),
            ]
        )
        self.assertTrue(previous_filmin_contracts)
        self.assertTrue(self.partner_id.has_had_filmin_service)

    def test_check_filmin_service_allowed(self):
        """Test that a partner with a Filmin contract raises an error
        when trying to create another Filmin service."""

        self.assertTrue(self.partner_id.has_had_filmin_service)

        self.assertRaisesRegex(
            ValidationError,
            "A Filmin contract already exists for this partner: %s."
            % self.partner_id.id,
            self.partner_id.check_filmin_service_allowed,
        )

    def test_has_not_had_filmin_service(self):
        """Test that a partner without a Filmin contract has the
        has_had_filmin_service field set to False."""

        partner_id = self.env.ref("somconnexio.res_partner_2_demo")
        previous_filmin_contracts = self.env["contract.contract"].search(
            [
                ("partner_id", "=", partner_id.id),
                (
                    "service_technology_id",
                    "=",
                    self.env.ref(
                        "multimedia_somconnexio.service_technology_multimedia"
                    ).id,
                ),
                (
                    "is_filmin",
                    "=",
                    True,
                ),
            ]
        )
        self.assertFalse(previous_filmin_contracts)
        self.assertFalse(partner_id.has_had_filmin_service)

    def test_check_filmin_service_allowed_no_previous_service(self):
        """Test that a partner without a Filmin contract does not raise an error
        when trying to create a Filmin service."""

        partner_id = self.env.ref("somconnexio.res_partner_2_demo")
        self.assertFalse(partner_id.has_had_filmin_service)

        # This should not raise an error
        partner_id.check_filmin_service_allowed()
