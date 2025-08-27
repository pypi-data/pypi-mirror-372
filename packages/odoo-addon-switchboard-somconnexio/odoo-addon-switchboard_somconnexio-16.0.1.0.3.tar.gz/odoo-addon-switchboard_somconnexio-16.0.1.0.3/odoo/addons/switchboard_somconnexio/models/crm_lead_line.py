from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    switchboard_isp_info = fields.Many2one(
        "switchboard.isp.info", string="Switchboard ISP Info"
    )
    is_switchboard = fields.Boolean(
        compute="_compute_is_switchboard",
        store=True,
    )

    switchboard_isp_info_icc = fields.Char(
        related="switchboard_isp_info.icc", store=True
    )
    switchboard_isp_info_type = fields.Selection(related="switchboard_isp_info.type")
    switchboard_isp_info_phone_number = fields.Char(
        related="switchboard_isp_info.phone_number"
    )
    switchboard_isp_info_extension = fields.Char(
        related="switchboard_isp_info.extension"
    )
    switchboard_isp_info_invoice_street = fields.Char(
        related="switchboard_isp_info.invoice_street"
    )
    switchboard_isp_info_invoice_zip_code = fields.Char(
        related="switchboard_isp_info.invoice_zip_code"
    )
    switchboard_isp_info_invoice_city = fields.Char(
        related="switchboard_isp_info.invoice_city"
    )
    switchboard_isp_info_invoice_state_id = fields.Many2one(
        "res.country.state", related="switchboard_isp_info.invoice_state_id"
    )
    switchboard_isp_info_delivery_street = fields.Char(
        related="switchboard_isp_info.delivery_street"
    )
    switchboard_isp_info_delivery_zip_code = fields.Char(
        related="switchboard_isp_info.delivery_zip_code"
    )
    switchboard_isp_info_delivery_city = fields.Char(
        related="switchboard_isp_info.delivery_city"
    )
    switchboard_isp_info_delivery_state_id = fields.Many2one(
        "res.country.state", related="switchboard_isp_info.delivery_state_id"
    )
    switchboard_isp_info_has_sim = fields.Boolean(
        related="switchboard_isp_info.has_sim",
    )

    @api.depends("product_id")
    def _compute_is_switchboard(self):
        service_SB = self.env.ref("switchboard_somconnexio.switchboard_category")
        for record in self:
            record.is_switchboard = (
                service_SB.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.onchange("switchboard_isp_info_icc")
    def _onchange_switchboard_icc(self):
        icc_change = {"icc": self.switchboard_isp_info_icc}
        if isinstance(self.id, models.NewId):
            self._origin.switchboard_isp_info.write(icc_change)
        else:
            self.switchboard_isp_info.write(icc_change)

    @api.constrains("is_switchboard", "switchboard_isp_info")
    def _check_isp_info(self):
        for record in self:
            if record.is_switchboard and not record.switchboard_isp_info:
                raise ValidationError(
                    _(
                        "A switchboard lead line needs a Switchboard "
                        + "ISP Info instance related."
                    )
                )

    @api.depends("switchboard_isp_info_type")
    def _compute_crm_creation_reason(self):
        super(CRMLeadLine, self)._compute_crm_creation_reason()
        for line in self:
            if not line.create_reason and line.switchboard_isp_info_type:
                line.create_reason = line.switchboard_isp_info_type

    def _get_formview_id(self):
        if self.env.context.get("is_switchboard"):
            return self.env.ref(
                "switchboard_somconnexio.view_form_lead_line_switchboard"
            ).id
        return super(CRMLeadLine, self)._get_formview_id()
