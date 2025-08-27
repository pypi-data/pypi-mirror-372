from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class SwitchboardISPInfoTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.switchboard_isp_info_args = {
            "type": "new",
            "agent_name": "test",
            "agent_email": "test@test.org",
            "icc": "7338161489147",
            "has_sim": True,
            "extension": "1234",
            "phone_number": "999999999",
            "phone_number_2": "999999998",
        }

    def test_new_creation_ok(self):
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            self.switchboard_isp_info_args
        )

        self.assertTrue(switchboard_isp_info.id)
        self.assertEqual(
            switchboard_isp_info.type, self.switchboard_isp_info_args["type"]
        )
        self.assertEqual(
            switchboard_isp_info.agent_name,
            self.switchboard_isp_info_args["agent_name"],
        )
        self.assertEqual(
            switchboard_isp_info.agent_email,
            self.switchboard_isp_info_args["agent_email"],
        )
        self.assertEqual(
            switchboard_isp_info.icc, self.switchboard_isp_info_args["icc"]
        )
        self.assertTrue(switchboard_isp_info.has_sim)
        self.assertEqual(
            switchboard_isp_info.extension, self.switchboard_isp_info_args["extension"]
        )
        self.assertEqual(
            switchboard_isp_info.phone_number,
            self.switchboard_isp_info_args["phone_number"],
        )
        self.assertEqual(
            switchboard_isp_info.phone_number_2,
            self.switchboard_isp_info_args["phone_number_2"],
        )
