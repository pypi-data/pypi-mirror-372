from odoo.tests.common import TransactionCase
import markupsafe


class TestContractAddressChangeWizard(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.env.ref("somconnexio.res_partner_1_demo")
        self.contract = self.env.ref("somconnexio.contract_fibra_600")

    def test_wizard_address_change_ok(self):
        wizard = (
            self.env["contract.address.change.wizard"]
            .with_context(active_id=self.contract.id)
            .create(
                {
                    "partner_bank_id": self.partner.bank_ids.id,
                    "service_street": "Carrer Nou 123",
                    "service_street2": "Principal A",
                    "service_zip_code": "00123",
                    "service_city": "Barcelona",
                    "service_state_id": self.ref("base.state_es_b"),
                    "service_country_id": self.ref("base.es"),
                    "previous_product_id": self.ref("somconnexio.Fibra600Mb"),
                    "product_id": self.ref("somconnexio.Fibra1Gb"),
                    "notes": "This is a random note",
                    "keep_phone_number": True,
                }
            )
        )

        crm_lead_action = wizard.button_change()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])

        self.assertEqual(
            crm_lead_action.get("xml_id"), "somconnexio.crm_case_form_view_pack"
        )
        self.assertEqual(crm_lead.name, "Change Address process")
        self.assertEqual(crm_lead.partner_id, self.partner)
        crm_lead_line = crm_lead.lead_line_ids[0]
        self.assertEqual(crm_lead_line.iban, self.partner.bank_ids.sanitized_acc_number)
        self.assertEqual(
            crm_lead_line.broadband_isp_info.service_street, "Carrer Nou 123"
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.service_street2, "Principal A"
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.service_zip_code, "00123")
        self.assertEqual(crm_lead_line.broadband_isp_info.service_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.broadband_isp_info.service_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.service_country_id,
            self.browse_ref("base.es"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.service_supplier_id,
            self.contract.service_supplier_id,
        )
        self.assertEqual(
            crm_lead_line.product_id, self.browse_ref("somconnexio.Fibra1Gb")
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_contract_address,
            "{}, {} - {} ({})".format(
                self.contract.service_partner_id.full_street,
                self.contract.service_partner_id.city,
                self.contract.service_partner_id.zip,
                self.contract.service_partner_id.state_id.name,
            ),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_contract_fiber_speed, "600 Mb"
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.previous_contract_pon, "")
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_owner_first_name,
            self.partner.firstname,
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_owner_name, self.partner.lastname
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_owner_vat_number, self.partner.vat
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_contract_phone,
            self.contract.phone_number,
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.phone_number, self.contract.phone_number
        )
        self.assertEqual(
            crm_lead.description, markupsafe.Markup("<p>This is a random note</p>")
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_provider.id,
            self.ref("somconnexio.previousprovider52"),
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.keep_phone_number, True)

    def test_wizard_address_change_with_pack(self):
        contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        wizard = (
            self.env["contract.address.change.wizard"]
            .with_context(active_id=contract.id)
            .create(
                {
                    "partner_bank_id": self.partner.bank_ids.id,
                    "service_street": "Carrer Nou 123",
                    "service_street2": "Principal A",
                    "service_zip_code": "00123",
                    "service_city": "Barcelona",
                    "service_state_id": self.ref("base.state_es_b"),
                    "service_country_id": self.ref("base.es"),
                    "previous_product_id": self.ref("somconnexio.Fibra600Mb"),
                    "product_id": self.ref("somconnexio.Fibra1Gb"),
                    "notes": "This is a random note",
                }
            )
        )

        crm_lead_action = wizard.button_change()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(len(crm_lead_line.broadband_isp_info.mobile_pack_contracts), 1)

    def test_default_get_partner_bank_id(self):
        context = {"active_id": self.contract.id}
        defaults = (
            self.env["contract.address.change.wizard"]
            .with_context(context)
            .default_get("partner_bank_id")
        )

        self.assertEqual(
            defaults["partner_bank_id"], self.contract.mandate_id.partner_bank_id.id
        )
