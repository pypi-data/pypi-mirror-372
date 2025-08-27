from faker import Faker
from odoo.addons.somconnexio.tests.helper_service import (
    crm_lead_create as _crm_lead_create,
    random_icc,
    random_mobile_phone,
    random_landline_number,
    random_ref,
)

faker = Faker("es_CA")


def crm_lead_create(
    odoo_env,
    partner_id,
    service_category,
    portability=False,
):
    if service_category != "switchboard":
        return _crm_lead_create(odoo_env, partner_id, service_category, portability)
    crm_lead_line = _sb_crm_lead_line_create(odoo_env, portability)
    crm_lead = odoo_env["crm.lead"].create(
        {
            "name": "Test Lead",
            "partner_id": partner_id.id,
            "phone": random_mobile_phone(),
            "email_from": faker.email(),
            "stage_id": odoo_env.ref("crm.stage_lead1").id,
        }
    )
    crm_lead.lead_line_ids = [(4, crm_lead_line.id)]
    return crm_lead


def _sb_crm_lead_line_create(odoo_env, portability):
    base_isp_info_args = (
        {
            "type": "portability",
            "previous_owner_vat_number": faker.vat_id(),
            "previous_owner_name": faker.first_name(),
            "previous_owner_first_name": faker.last_name(),
        }
        if portability
        else {"type": "new"}
    )
    switchboard_isp_info_args = {
        "phone_number_2": random_landline_number(),
        "extension": random_ref(),
        "icc": random_icc(odoo_env),
        "agent_name": faker.name(),
        "agent_email": faker.email(),
    }
    isp_info = odoo_env["switchboard.isp.info"].create(
        dict(**base_isp_info_args, **switchboard_isp_info_args)
    )
    product = odoo_env.ref("switchboard_somconnexio.AgentCentraletaVirtualApp500")
    crm_lead_line_args = {
        "name": "CRM Lead",
        "iban": faker.iban(),
        "product_id": product.id,
        "switchboard_isp_info": isp_info.id,
    }

    return odoo_env["crm.lead.line"].create(crm_lead_line_args)
