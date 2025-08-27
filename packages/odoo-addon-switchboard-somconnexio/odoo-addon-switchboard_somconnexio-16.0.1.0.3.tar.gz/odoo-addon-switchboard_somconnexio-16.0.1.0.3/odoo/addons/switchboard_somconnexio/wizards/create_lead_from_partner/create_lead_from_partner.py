from odoo import models, fields


class CreateLeadFromPartnerWizard(models.TransientModel):
    _inherit = "partner.create.lead.wizard"

    agent_name = fields.Char("Agent name")
    agent_email = fields.Char("Agent email")
    extension = fields.Char("Extension")
    landline_2 = fields.Char("Landline 2")

    def _create_isp_info_params(self):
        if self.product_categ_id != self.env.ref(
            "switchboard_somconnexio.switchboard_category"
        ):
            return super()._create_isp_info_params()

        isp_info_model_name = "switchboard.isp.info"
        isp_info_args = {
            "type": self.type,
            "agent_name": self.agent_name,
            "agent_email": self.agent_email,
            "extension": self.extension,
            "icc": self.icc,
            "phone_number": self.landline,
            "phone_number_2": self.landline_2,
        }
        isp_info_address_args = {
            "delivery_street": self.delivery_street,
            "delivery_zip_code": self.delivery_zip_code,
            "delivery_city": self.delivery_city,
            "delivery_state_id": self.delivery_state_id.id,
            "delivery_country_id": self.delivery_country_id.id,
            "invoice_street": self.invoice_street,
            "invoice_zip_code": self.invoice_zip_code,
            "invoice_city": self.invoice_city,
            "invoice_state_id": self.invoice_state_id.id,
            "invoice_country_id": self.invoice_country_id.id,
        }

        isp_info_res_id = self.env[isp_info_model_name].create(
            {**isp_info_args, **isp_info_address_args}
        )
        return isp_info_model_name, isp_info_res_id
