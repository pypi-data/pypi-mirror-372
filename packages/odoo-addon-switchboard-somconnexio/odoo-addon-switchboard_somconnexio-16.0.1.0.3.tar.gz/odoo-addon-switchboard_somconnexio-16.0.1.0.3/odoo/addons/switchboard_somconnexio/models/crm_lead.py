from odoo import models, fields, api
import json


class CRMLead(models.Model):
    _inherit = "crm.lead"

    switchboard_lead_line_ids = fields.One2many(
        "crm.lead.line",
        string="Switchboard lead lines",
        compute="_compute_sb_lead_line_ids",
    )
    has_switchboard_lead_lines = fields.Boolean(
        compute="_compute_has_switchboard_lead_lines", store=True
    )

    @api.depends("lead_line_ids")
    def _compute_sb_lead_line_ids(self):
        for crm in self:
            crm.switchboard_lead_line_ids = crm.lead_line_ids.filtered(
                lambda p: p.is_switchboard
            )

    @api.depends("switchboard_lead_line_ids")
    def _compute_has_switchboard_lead_lines(self):
        for crm in self:
            crm.has_switchboard_lead_lines = bool(crm.switchboard_lead_line_ids)

    @api.depends("has_switchboard_lead_lines")
    def _compute_phones_from_lead(self):
        super()._compute_phones_from_lead()
        for crm in self:
            if crm.has_switchboard_lead_lines:
                non_sb_phones_from_lead = json.loads(crm.phones_from_lead)
                crm.phones_from_lead = (
                    crm.switchboard_lead_line_ids.mapped(
                        "switchboard_isp_info_phone_number"
                    )
                    + non_sb_phones_from_lead
                )
