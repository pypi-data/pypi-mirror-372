from odoo import models, fields


class SwitchboardServiceContractInfo(models.Model):
    _name = "switchboard.service.contract.info"
    _inherit = "base.service.contract.info"
    _description = "Switchboard Contract Service Info"

    contract_ids = fields.One2many(
        "contract.contract", "switchboard_service_contract_info_id", "Contracts"
    )
    phone_number_2 = fields.Char("Second landline phone number")
    agent_name = fields.Char("Agent name")
    agent_email = fields.Char("Agent web user")
    extension = fields.Char("Extension")
    mobile_phone_number = fields.Char("CV mobile phone number")
    icc = fields.Char("ICC")
    MAC_CPE_SIP = fields.Char("MAC CPE SIP")
    SIP_channel_name = fields.Char("SIP channel name")
    SIP_channel_password = fields.Char("SIP channel password")
