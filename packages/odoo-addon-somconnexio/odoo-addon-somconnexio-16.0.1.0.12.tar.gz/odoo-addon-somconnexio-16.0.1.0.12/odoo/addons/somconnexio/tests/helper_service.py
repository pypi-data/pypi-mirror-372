from faker import Faker
import random

faker = Faker("es_CA")


def random_icc(odoo_env):
    icc_prefix = odoo_env["ir.config_parameter"].get_param(
        "somconnexio.icc_start_sequence"
    )
    random_part = [str(random.randint(0, 9)) for _ in range(19 - len(icc_prefix))]
    return icc_prefix + "".join(random_part)


def random_ref():
    return str(random.randint(0, 99999))


def random_mobile_phone():
    """
    Returns a random 9 digit number starting with either 6 or 7
    """
    return str(random.randint(6, 7)) + str(random.randint(10000000, 99999999))


def random_landline_number():
    """
    Returns a random 9 digit number starting with either 8 or 9
    """
    return str(random.randint(8, 9)) + str(random.randint(10000000, 99999999))


def partner_create_data(odoo_env):
    return {
        "parent_id": False,
        "name": faker.name(),
        "email": faker.email(),
        "street": faker.street_address(),
        "street2": faker.street_address(),
        "city": faker.city(),
        "zip_code": faker.postcode(),
        "country_id": odoo_env.ref("base.es"),
        "state_id": odoo_env.ref("base.state_es_b"),
        "customer": True,
        "ref": random_ref(),
        "lang": random.choice(["es_ES", "ca_ES"]),
    }


def crm_lead_line_create(
    odoo_env, service_category, portability, shared_bond_id="ABC1234"
):
    product_switcher = {
        "mobile": odoo_env.ref("somconnexio.TrucadesIllimitades20GB"),
        "pack": odoo_env.ref("somconnexio.TrucadesIllimitades30GBPack"),
        "shared_data": odoo_env.ref("somconnexio.50GBCompartides2mobils"),
        "fiber": odoo_env.ref("somconnexio.Fibra100Mb"),
        "adsl": odoo_env.ref("somconnexio.ADSL20MBSenseFix"),
        "4G": odoo_env.ref("somconnexio.Router4G"),
    }
    base_isp_info_args = (
        {
            "type": "portability",
            "previous_provider": odoo_env.ref("somconnexio.previousprovider39").id,
            "previous_owner_vat_number": faker.vat_id(),
            "previous_owner_name": faker.first_name(),
            "previous_owner_first_name": faker.last_name(),
        }
        if portability
        else {"type": "new"}
    )
    base_ba_isp_info_args = {
        "service_full_street": faker.address(),
        "service_city": faker.city(),
        "service_zip_code": "08015",
        "service_state_id": odoo_env.ref("base.state_es_b").id,
        "service_country_id": odoo_env.ref("base.es").id,
    }
    base_mbl_isp_info_args = {
        "phone_number": random_mobile_phone(),
        "icc": random_icc(odoo_env),
        "previous_contract_type": "contract",
    }
    isp_info_args_switcher = {
        "mobile": base_mbl_isp_info_args,
        "pack": base_mbl_isp_info_args,
        "shared_data": dict(**base_mbl_isp_info_args, shared_bond_id=shared_bond_id),
        "fiber": dict(**base_ba_isp_info_args, phone_number=random_landline_number()),
        "adsl": dict(**base_ba_isp_info_args, phone_number=random_landline_number()),
        "4G": dict(**base_ba_isp_info_args, phone_number="-"),
    }
    model_switcher = {
        "mobile": "mobile.isp.info",
        "pack": "mobile.isp.info",
        "shared_data": "mobile.isp.info",
        "fiber": "broadband.isp.info",
        "adsl": "broadband.isp.info",
        "4G": "broadband.isp.info",
    }
    isp_info = odoo_env[model_switcher[service_category]].create(
        dict(**base_isp_info_args, **isp_info_args_switcher[service_category])
    )
    crm_lead_line_args = {
        "name": "CRM Lead",
        "iban": faker.iban(),
        "product_id": product_switcher[service_category].id,
    }
    if service_category in ["fiber", "adsl", "4G"]:
        crm_lead_line_args.update(
            {
                "broadband_isp_info": isp_info.id,
            }
        )
    else:
        crm_lead_line_args.update(
            {
                "mobile_isp_info": isp_info.id,
            }
        )

    return odoo_env["crm.lead.line"].create(crm_lead_line_args)


def crm_lead_create(
    odoo_env,
    partner_id,
    service_category,
    portability=False,
):
    if service_category in ["mobile", "fiber", "adsl", "4G"]:
        crm_lead_line_ids = crm_lead_line_create(
            odoo_env, service_category, portability
        )
    elif service_category == "pack":
        crm_lead_line_ids = crm_lead_line_create(
            odoo_env, "fiber", portability
        ) + crm_lead_line_create(odoo_env, service_category, portability)
    elif service_category == "shared_data":
        crm_lead_line_ids = (
            crm_lead_line_create(odoo_env, "fiber", portability)
            + crm_lead_line_create(odoo_env, service_category, portability)
            + crm_lead_line_create(odoo_env, service_category, portability)
        )

    iban = random.choice(partner_id.bank_ids.mapped("sanitized_acc_number"))
    for crm_lead_line in crm_lead_line_ids:
        crm_lead_line.write({"iban": iban})

    return odoo_env["crm.lead"].create(
        {
            "name": "Test Lead",
            "partner_id": partner_id.id,
            "lead_line_ids": [(6, 0, crm_lead_line_ids.ids)],
            "stage_id": odoo_env.ref("crm.stage_lead1").id,
        }
    )


def contract_mobile_create_data(odoo_env, partner):
    mobile_contract_service_info = odoo_env["mobile.service.contract.info"].create(
        {"phone_number": random_mobile_phone(), "icc": random_icc(odoo_env)}
    )
    vals = contract_create_data(partner)
    vals.update(
        {
            "name": "Test Contract Mobile",
            "service_technology_id": odoo_env.ref(
                "somconnexio.service_technology_mobile"
            ).id,
            "service_supplier_id": odoo_env.ref(
                "somconnexio.service_supplier_masmovil"
            ).id,
            "mobile_contract_service_info_id": (mobile_contract_service_info.id),
        }
    )
    return vals


def contract_adsl_create_data(odoo_env, partner):
    router_product = odoo_env.ref("somconnexio.RouterModelNCDS224WTV")
    # router_lot = odoo_env["stock.production.lot"].create(
    #     {
    #         "product_id": router_product.id,
    #         "name": faker.user_name(),
    #         "router_mac_address": faker.mac_address(),
    #     }
    # )
    adsl_contract_service_info = odoo_env["adsl.service.contract.info"].create(
        {
            "phone_number": random_mobile_phone(),
            "administrative_number": str(random.randint(000, 999)),
            "router_product_id": router_product.id,
            # "router_lot_id": router_lot.id,
            "ppp_user": faker.user_name(),
            "ppp_password": faker.password(),
            "endpoint_user": faker.user_name(),
            "endpoint_password": faker.password(),
        }
    )
    vals = contract_create_data(partner)
    vals.update(
        {
            "name": "Test Contract Broadband",
            "service_technology_id": odoo_env.ref(
                "somconnexio.service_technology_adsl"
            ).id,
            "service_supplier_id": odoo_env.ref(
                "somconnexio.service_supplier_jazztel"
            ).id,
            "adsl_service_contract_info_id": (adsl_contract_service_info.id),
        }
    )
    return vals


def contract_fiber_create_data(odoo_env, partner, provider="vodafone"):
    vals = contract_create_data(partner)
    vals.update(
        {
            "name": "Test Contract Broadband",
            "service_technology_id": odoo_env.ref(
                "somconnexio.service_technology_fiber"
            ).id,
        }
    )
    if provider == "vodafone":
        vodafone_fiber_contract_service_info = odoo_env[
            "vodafone.fiber.service.contract.info"
        ].create(
            {
                "phone_number": random_landline_number(),
                "vodafone_id": str(random.randint(000, 999)),
                "vodafone_offer_code": str(random.randint(0000, 9999)),
            }
        )
        vals.update(
            {
                "service_supplier_id": odoo_env.ref(
                    "somconnexio.service_supplier_vodafone"
                ).id,
                "vodafone_fiber_service_contract_info_id": (
                    vodafone_fiber_contract_service_info.id
                ),
            }
        )
    elif provider == "masmovil":
        mm_fiber_service_contract_info = odoo_env[
            "mm.fiber.service.contract.info"
        ].create(
            {
                "phone_number": random_landline_number(),
                "mm_id": str(random.randint(000, 999)),
                "previous_id": str(random.randint(0000, 9999)),
            }
        )
        vals.update(
            {
                "service_supplier_id": odoo_env.ref(
                    "somconnexio.service_supplier_masmovil"
                ).id,
                "mm_fiber_service_contract_info_id": (
                    mm_fiber_service_contract_info.id
                ),
            }
        )
    elif provider == "xoln":
        router_product = odoo_env.ref("somconnexio.RouterModelNCDS224WTV")
        # UNCOMMENT Pending of review the router_lot
        # router_lot = odoo_env["stock.production.lot"].create(
        #     {
        #         "product_id": router_product.id,
        #         "name": faker.user_name(),
        #         "router_mac_address": faker.mac_address(),
        #     }
        # )
        xoln_fiber_service_contract_info = odoo_env[
            "xoln.fiber.service.contract.info"
        ].create(
            {
                "phone_number": random_landline_number(),
                "external_id": str(random.randint(0000, 9999)),
                "project_id": odoo_env.ref("somconnexio.xoln_project_borda").id,
                "id_order": str(random.randint(0000, 9999)),
                "router_product_id": router_product.id,
                # "router_lot_id": router_lot.id,
            }
        )
        vals.update(
            {
                "xoln_fiber_service_contract_info_id": (
                    xoln_fiber_service_contract_info.id
                ),
                "service_supplier_id": odoo_env.ref(
                    "somconnexio.service_supplier_xoln"
                ).id,
            }
        )
    return vals


def contract_4g_create_data(odoo_env, partner):
    router_4g_service_contract_info = odoo_env[
        "router.4g.service.contract.info"
    ].create(
        {
            "vodafone_id": str(random.randint(000, 999)),
            "vodafone_offer_code": str(random.randint(0000, 9999)),
            "icc": random_icc(odoo_env),
        }
    )
    vals = contract_create_data(partner)
    vals.update(
        {
            "name": "Test Contract 4G",
            "service_technology_id": odoo_env.ref(
                "somconnexio.service_technology_4G"
            ).id,
            "service_supplier_id": odoo_env.ref(
                "somconnexio.service_supplier_vodafone"
            ).id,
            "router_4G_service_contract_info_id": (router_4g_service_contract_info.id),
        }
    )
    return vals


def contract_create_data(partner):
    return {
        "partner_id": partner.id,
        "service_partner_id": partner.id,
        "invoice_partner_id": partner.id,
        "email_ids": [(4, partner.id, 0)],
        "mandate_id": partner.bank_ids[0].mandate_ids[0].id,
    }
