from odoo import models, fields, api


class SwitchboardISPInfo(models.Model):
    _name = "switchboard.isp.info"
    _inherit = "base.isp.info"
    _description = "Switchboard ISP Info"

    phone_number_2 = fields.Char("Second landline phone number")
    agent_name = fields.Char("Agent name", required=True)
    agent_email = fields.Char("Agent email")
    extension = fields.Char("Extension", required=True)
    icc = fields.Char("ICC")
    has_sim = fields.Boolean(string="Has sim card", default=False)

    @api.constrains("type", "previous_provider")
    def _check_portability_info(self):
        """
        TODO: Switchboard portabilities do not need
        previous providers so far.
        If eventually they do, remove this
        """
        return True
