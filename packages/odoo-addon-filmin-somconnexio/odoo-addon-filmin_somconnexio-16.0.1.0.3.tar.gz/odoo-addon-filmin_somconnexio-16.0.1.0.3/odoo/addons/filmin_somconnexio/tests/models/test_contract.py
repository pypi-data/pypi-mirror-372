from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContract(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.contract = self.env.ref("filmin_somconnexio.contract_filmin")

    def test_is_filmin(self):
        self.assertTrue(self.contract.is_filmin)

    def test_is_not_filmin(self):
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.assertFalse(contract.is_filmin)

    def test_contract_name(self):
        self.assertEqual(
            self.contract.name, f"FILMIN - {self.contract.subscription_code}"
        )

    def test_contract_type(self):
        self.assertEqual(self.contract.service_contract_type, "filmin")

    def test_contract_type_not_filmin(self):
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.assertNotEqual(contract.service_contract_type, "filmin")

    def test_filmin_contract_to_dict(self):
        self.assertEqual(self.contract._to_dict()["subscription_technology"], "filmin")
