from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class CRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.partner_iban = self.partner_id.bank_ids[0].sanitized_acc_number
        self.product_sb = self.env.ref(
            "switchboard_somconnexio.AgentCentraletaVirtualApp500"
        )

        self.crm_lead_line_args = {
            "name": "Test SB CRM Lead Line",
            "product_id": self.product_sb.id,
            "mobile_isp_info": None,
            "broadband_isp_info": None,
            "switchboard_isp_info": None,
            "iban": self.partner_iban,
        }

    def test_sb_lead_line_creation_ok(self):
        switchboard_isp_info_args = {
            "type": "new",
            "agent_name": "Test Agent",
            "extension": "123456789",
        }
        switchboard_isp_info = self.env["switchboard.isp.info"].create(
            switchboard_isp_info_args
        )
        self.crm_lead_line_args.update(
            {
                "switchboard_isp_info": switchboard_isp_info.id,
            }
        )

        sb_crm_lead_line = self.env["crm.lead.line"].create([self.crm_lead_line_args])
        self.assertTrue(sb_crm_lead_line.id)
        self.assertTrue(sb_crm_lead_line.is_switchboard)
        self.assertEqual(sb_crm_lead_line.iban, self.partner_iban)
        self.assertEqual(sb_crm_lead_line.create_reason, switchboard_isp_info.type)

    def test_sb_lead_line_creation_without_sb_isp_info(self):
        self.assertRaises(
            ValidationError, self.env["crm.lead.line"].create, [self.crm_lead_line_args]
        )
