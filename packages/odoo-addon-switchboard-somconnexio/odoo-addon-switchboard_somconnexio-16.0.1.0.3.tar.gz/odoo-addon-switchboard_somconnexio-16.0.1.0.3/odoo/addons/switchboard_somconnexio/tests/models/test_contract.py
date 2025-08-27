from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContract(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.switchboard_contract = self.env.ref(
            "switchboard_somconnexio.contract_switchboard_app_500"
        )

    def test_contract_name(self, *args):
        self.assertEqual(self.switchboard_contract.name, "965587599 - 456")
        self.switchboard_contract.switchboard_service_contract_info_id.write(
            {"phone_number": "AAAAAAAA", "extension": "BBBBBBB"}
        )
        self.assertEqual(self.switchboard_contract.name, "AAAAAAAA - BBBBBBB")
