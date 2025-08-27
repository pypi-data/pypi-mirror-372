from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    switchboard_service_contract_info_id = fields.Many2one(
        "switchboard.service.contract.info",
        domain=[("id", "=", 0)],
        string="Service Contract Info",
    )
    switchboard_mobile = fields.Char(
        "Switchboard mobile phone number",
        related="switchboard_service_contract_info_id.mobile_phone_number",
    )

    @api.depends("phone_number")
    def _compute_name(self):
        super(Contract, self)._compute_name()
        for contract in self:
            if contract.service_contract_type == "switchboard":
                extension = contract.switchboard_service_contract_info_id.extension
                contract.name = f"{contract.phone_number} - {extension}"

    @api.depends(
        "service_contract_type",
        "switchboard_service_contract_info_id.phone_number",
    )
    def _compute_phone_number(self):
        super(Contract, self)._compute_phone_number()
        for contract in self:
            if contract.service_contract_type == "switchboard":
                contract.phone_number = (
                    contract.switchboard_service_contract_info_id.phone_number
                )

    @api.depends("service_technology_id")
    def _compute_contract_type(self):
        super(Contract, self)._compute_contract_type()
        switchboard = self.env.ref(
            "switchboard_somconnexio.service_technology_switchboard"
        )

        for record in self:
            if record.service_technology_id == switchboard:
                record.service_contract_type = "switchboard"

    def _tariff_contract_line(self, field, current):
        super(Contract, self)._tariff_contract_line(field, current)

        switchboard = self.env.ref(
            "switchboard_somconnexio.service_technology_switchboard"
        )
        for contract in self:
            if contract.service_technology_id != switchboard:
                continue

            for line in contract.contract_line_ids:
                if line.product_id.categ_id == self.env.ref(
                    "switchboard_somconnexio.switchboard_category"
                ) and (contract._is_contract_line_active(line) or not current):
                    setattr(contract, field, line)
                    break
