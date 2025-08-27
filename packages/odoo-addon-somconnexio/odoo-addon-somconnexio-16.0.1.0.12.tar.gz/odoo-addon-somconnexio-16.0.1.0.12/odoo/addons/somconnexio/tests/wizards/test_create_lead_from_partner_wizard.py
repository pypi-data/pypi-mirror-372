from mock import patch

from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError, MissingError


@patch(
    "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
)
class TestCreateLeadfromPartnerWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.mbl_categ = self.env.ref("somconnexio.mobile_service")
        self.fiber_categ = self.env.ref("somconnexio.broadband_fiber_service")
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.bank = self.partner.bank_ids[0]
        self.email = self.env["res.partner"].create(
            {
                "parent_id": self.partner.id,
                "email": "new_email@test.com",
                "type": "contract-email",
            }
        )
        self.partner.phone = "888888888"

        self.wizard_params = {
            "opportunity": "test new mobile with invoice address",
            "bank_id": self.partner.bank_ids.id,
            "email_id": self.email.id,
            "product_id": self.ref("somconnexio.SenseMinuts2GB"),
            "product_categ_id": self.mbl_categ.id,
            "type": "new",
            "delivery_street": "Principal A",
            "delivery_zip_code": "08027",
            "delivery_city": "Barcelona",
            "delivery_state_id": self.ref("base.state_es_b"),
            "invoice_street": "Principal B",
            "invoice_zip_code": "08015",
            "invoice_city": "Barcelona",
            "invoice_state_id": self.ref("base.state_es_b"),
        }
        self.service_address = {
            "service_street": "Principal A",
            "service_zip_code": "00123",
            "service_city": "Barcelona",
            "service_state_id": self.ref("base.state_es_b"),
        }

    def test_create_new_mobile_lead_with_icc(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.wizard_params["icc"] = "666"

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        self.assertFalse(wizard.is_service_address_required)
        self.assertFalse(wizard.is_delivery_address_required)
        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            crm_lead_action.get("xml_id"), "somconnexio.crm_case_form_view_pack"
        )

        self.assertEqual(crm_lead.name, "test new mobile with invoice address")
        self.assertEqual(crm_lead.partner_id, self.partner)
        self.assertEqual(crm_lead.email_from, self.email.email)
        self.assertEqual(crm_lead_line.mobile_isp_info.icc, "666")
        self.assertEqual(crm_lead_line.mobile_isp_info.type, "new")
        self.assertEqual(
            crm_lead_line.product_id, self.browse_ref("somconnexio.SenseMinuts2GB")
        )
        self.assertEqual(crm_lead_line.iban, self.partner.bank_ids.sanitized_acc_number)
        self.assertEqual(crm_lead_line.mobile_isp_info.invoice_street, "Principal B")
        self.assertEqual(crm_lead_line.mobile_isp_info.invoice_zip_code, "08015")
        self.assertEqual(crm_lead_line.mobile_isp_info.invoice_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_country_id, self.browse_ref("base.es")
        )
        self.assertFalse(
            crm_lead_line.mobile_isp_info.linked_fiber_contract_id,
        )

    def test_create_new_mobile_lead_without_icc(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        self.assertFalse(wizard.is_service_address_required)
        self.assertTrue(wizard.is_delivery_address_required)

        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            crm_lead_action.get("xml_id"), "somconnexio.crm_case_form_view_pack"
        )

        self.assertEqual(crm_lead.name, "test new mobile with invoice address")
        self.assertEqual(crm_lead.partner_id, self.partner)
        self.assertEqual(crm_lead.email_from, self.email.email)
        self.assertEqual(crm_lead_line.mobile_isp_info.type, "new")
        self.assertEqual(
            crm_lead_line.product_id, self.browse_ref("somconnexio.SenseMinuts2GB")
        )
        self.assertEqual(crm_lead_line.iban, self.partner.bank_ids.sanitized_acc_number)
        self.assertEqual(crm_lead_line.mobile_isp_info.delivery_street, "Principal A")
        self.assertEqual(crm_lead_line.mobile_isp_info.delivery_zip_code, "08027")
        self.assertEqual(crm_lead_line.mobile_isp_info.delivery_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_country_id,
            self.browse_ref("base.es"),
        )
        self.assertEqual(crm_lead_line.mobile_isp_info.invoice_street, "Principal B")
        self.assertEqual(crm_lead_line.mobile_isp_info.invoice_zip_code, "08015")
        self.assertEqual(crm_lead_line.mobile_isp_info.invoice_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.invoice_country_id, self.browse_ref("base.es")
        )
        self.assertFalse(
            crm_lead_line.mobile_isp_info.linked_fiber_contract_id,
        )

    def test_create_portability_mobile_lead(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.wizard_params.update(
            {
                "opportunity": "test portability mobile",
                "icc": "666",
                "type": "portability",
                "previous_contract_type": "contract",
                "phone_number": "666666666",
                "donor_icc": "3333",
                "previous_mobile_provider": self.ref("somconnexio.previousprovider4"),
                "previous_owner_vat_number": "52736216E",
                "previous_owner_first_name": "Firstname test",
                "previous_owner_name": "Lastname test",
            }
        )
        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )
        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            wizard.available_products,
            self.env["product.product"].search(
                self._get_expected_product_domain(wizard.product_categ_id)
            ),
        )

        self.assertEqual(
            crm_lead_action.get("xml_id"), "somconnexio.crm_case_form_view_pack"
        )

        self.assertEqual(crm_lead.name, "test portability mobile")
        self.assertEqual(crm_lead.partner_id, self.partner)
        self.assertEqual(crm_lead.email_from, self.email.email)
        self.assertEqual(crm_lead.team_id, self.env.ref("somconnexio.residential"))
        self.assertEqual(
            crm_lead_line.product_id, self.browse_ref("somconnexio.SenseMinuts2GB")
        )
        self.assertEqual(crm_lead_line.iban, self.partner.bank_ids.sanitized_acc_number)
        self.assertEqual(crm_lead_line.mobile_isp_info.icc, "666")
        self.assertEqual(crm_lead_line.mobile_isp_info.type, "portability")
        self.assertEqual(
            crm_lead_line.mobile_isp_info.previous_contract_type, "contract"
        )
        self.assertEqual(crm_lead_line.mobile_isp_info.phone_number, "666666666")
        self.assertEqual(crm_lead_line.mobile_isp_info.icc_donor, "3333")
        self.assertEqual(
            crm_lead_line.mobile_isp_info.previous_provider,
            self.browse_ref("somconnexio.previousprovider4"),
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.previous_owner_vat_number, "ES52736216E"
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.previous_owner_first_name, "Firstname test"
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.previous_owner_name, "Lastname test"
        )
        self.assertEqual(crm_lead_line.mobile_isp_info.delivery_street, "Principal A")
        self.assertEqual(crm_lead_line.mobile_isp_info.delivery_zip_code, "08027")
        self.assertEqual(crm_lead_line.mobile_isp_info.delivery_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.delivery_country_id,
            self.browse_ref("base.es"),
        )
        self.assertFalse(
            crm_lead_line.mobile_isp_info.linked_fiber_contract_id,
        )

    def test_create_new_mobile_lead_with_business_team(self, mock_get_fiber_contracts):
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        mock_get_fiber_contracts.return_value = [fiber_contract]

        business_team = self.env.ref("somconnexio.business")

        self.wizard_params.update(
            {
                "team_id": business_team.id,
            }
        )
        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )
        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])

        self.assertEqual(
            wizard.available_products,
            self.env["product.product"].search(
                self._get_expected_product_domain(
                    wizard.product_categ_id, pack_product=True, business=True
                )
            ),
        )
        self.assertEqual(crm_lead.team_id, business_team)

    def test_create_new_BA_lead(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.wizard_params.update(
            {
                "opportunity": "test new BA",
                "product_id": self.ref("somconnexio.Fibra600Mb"),
                "product_categ_id": self.fiber_categ.id,
                **self.service_address,
            }
        )

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        self.assertTrue(wizard.is_service_address_required)
        self.assertFalse(wizard.is_delivery_address_required)

        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            crm_lead_action.get("xml_id"), "somconnexio.crm_case_form_view_pack"
        )

        self.assertEqual(crm_lead.name, "test new BA")
        self.assertEqual(crm_lead.partner_id, self.partner)
        self.assertEqual(crm_lead.email_from, self.email.email)
        self.assertEqual(
            crm_lead_line.product_id, self.browse_ref("somconnexio.Fibra600Mb")
        )
        self.assertEqual(crm_lead_line.iban, self.partner.bank_ids.sanitized_acc_number)
        self.assertEqual(crm_lead_line.broadband_isp_info.type, "new")
        self.assertEqual(crm_lead_line.broadband_isp_info.service_street, "Principal A")
        self.assertEqual(crm_lead_line.broadband_isp_info.service_zip_code, "00123")
        self.assertEqual(crm_lead_line.broadband_isp_info.service_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.broadband_isp_info.service_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.delivery_country_id,
            self.browse_ref("base.es"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.delivery_street, "Principal A"
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.delivery_zip_code, "08027")
        self.assertEqual(crm_lead_line.broadband_isp_info.delivery_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.broadband_isp_info.delivery_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.delivery_country_id,
            self.browse_ref("base.es"),
        )

    def test_create_portability_BA_lead(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.wizard_params.update(
            {
                "opportunity": "test portability BA",
                "product_id": self.ref("somconnexio.Fibra600Mb"),
                "product_categ_id": self.fiber_categ.id,
                "type": "portability",
                "previous_owner_vat_number": "52736216E",
                "previous_owner_first_name": "Test",
                "previous_owner_name": "Test",
                "keep_landline": True,
                "landline": "972972972",
                "previous_BA_service": "fiber",
                "previous_BA_provider": self.ref("somconnexio.previousprovider3"),
                **self.service_address,
            }
        )

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            crm_lead_action.get("xml_id"), "somconnexio.crm_case_form_view_pack"
        )

        self.assertEqual(crm_lead.name, "test portability BA")
        self.assertEqual(crm_lead.partner_id, self.partner)
        self.assertEqual(crm_lead.email_from, self.email.email)
        self.assertEqual(
            crm_lead_line.product_id, self.browse_ref("somconnexio.Fibra600Mb")
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.type, "portability")
        self.assertTrue(crm_lead_line.broadband_isp_info.keep_phone_number)
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_provider,
            self.browse_ref("somconnexio.previousprovider3"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.previous_service,
            "fiber",
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.service_street, "Principal A")
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
            crm_lead_line.broadband_isp_info.delivery_street, "Principal A"
        )
        self.assertEqual(crm_lead_line.broadband_isp_info.delivery_zip_code, "08027")
        self.assertEqual(crm_lead_line.broadband_isp_info.delivery_city, "Barcelona")
        self.assertEqual(
            crm_lead_line.broadband_isp_info.delivery_state_id,
            self.browse_ref("base.state_es_b"),
        )
        self.assertEqual(
            crm_lead_line.broadband_isp_info.delivery_country_id,
            self.browse_ref("base.es"),
        )

    def test_create_portability_mobile_without_phone_number(
        self, mock_get_fiber_contracts
    ):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.wizard_params.update(
            {
                "opportunity": "test portability mobile",
                "icc": "666",
                "type": "portability",
                "previous_contract_type": "contract",
                "donor_icc": "3333",
                "previous_mobile_provider": self.ref("somconnexio.previousprovider4"),
                "previous_owner_vat_number": "52736216E",
                "previous_owner_first_name": "Firstname test",
                "previous_owner_name": "Lastname test",
            }
        )

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        self.assertRaises(ValidationError, wizard.create_lead)

    def test_create_portability_ba_keep_landline_without_number(
        self, mock_get_fiber_contracts
    ):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.wizard_params.update(
            {
                "opportunity": "test portability BA",
                "product_id": self.ref("somconnexio.Fibra600Mb"),
                "product_categ_id": self.fiber_categ.id,
                "type": "portability",
                "previous_owner_vat_number": "52736216E",
                "previous_owner_first_name": "Test",
                "previous_owner_name": "Test",
                "keep_landline": True,
                "previous_BA_service": "fiber",
                "previous_BA_provider": self.ref("somconnexio.previousprovider4"),
                **self.service_address,
            }
        )

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        self.assertRaises(ValidationError, wizard.create_lead)

    def test_set_phone_to_partner_if_none(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        self.partner.phone = False
        self.partner.mobile = False
        self.wizard_params["phone_contact"] = "666666666"

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )

        self.assertFalse(self.partner.phone)

        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])

        self.assertEqual(self.partner.phone, wizard.phone_contact)
        self.assertEqual(crm_lead.phone, wizard.phone_contact)

    def test_default_phone_contact_partner_mobile_over_phone(
        self, mock_get_fiber_contracts
    ):
        mock_get_fiber_contracts.side_effect = MissingError("")
        self.partner.mobile = "666777888"

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )
        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])

        self.assertEqual(wizard.phone_contact, self.partner.mobile)
        self.assertEqual(wizard.phone_contact, crm_lead.phone)

    def test_fiber_contract_to_link(self, mock_get_fiber_contracts):
        fiber_contract = self.env.ref("somconnexio.contract_fibra_600")
        mock_get_fiber_contracts.return_value = [fiber_contract]

        self.wizard_params.update(
            {
                "product_id": self.ref("somconnexio.TrucadesIllimitades20GBPack"),
            }
        )
        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=self.partner.id)
            .create(self.wizard_params)
        )
        crm_lead_action = wizard.create_lead()
        crm_lead = self.env["crm.lead"].browse(crm_lead_action["res_id"])
        crm_lead_line = crm_lead.lead_line_ids[0]

        self.assertEqual(
            crm_lead_line.mobile_isp_info.linked_fiber_contract_id, fiber_contract
        )
        self.assertEqual(
            wizard.available_products,
            self.env["product.product"].search(
                self._get_expected_product_domain(
                    wizard.product_categ_id, pack_product=True
                )
            ),
        )

    def _get_expected_product_domain(
        self, product_categ, pack_product=False, business=False
    ):
        product_templs = self.env["product.template"].search(
            [
                ("categ_id", "=", product_categ.id),
                ("name", "not ilike", "borda"),
            ]
        )
        expected_domain = [
            ("product_tmpl_id", "in", product_templs.ids),
            ("pack_ok", "=", False),
        ]

        attr_to_exclude = self.env["product.attribute.value"]
        attr_to_include = self.env["product.attribute.value"]

        if not pack_product:
            attr_to_exclude |= self.env.ref("somconnexio.IsInPack")
        if business:
            attr_to_include |= self.env.ref("somconnexio.CompanyExclusive")
        else:
            attr_to_exclude |= self.env.ref("somconnexio.CompanyExclusive")

        if attr_to_exclude:
            expected_domain.extend(
                [
                    (
                        "product_template_attribute_value_ids.product_attribute_value_id",  # noqa
                        "not in",
                        attr_to_exclude.ids,
                    ),
                ]
            )
        if attr_to_include:
            expected_domain.extend(
                [
                    (
                        "product_template_attribute_value_ids.product_attribute_value_id",  # noqa
                        "in",
                        attr_to_include.ids,
                    ),
                ]
            )

        return expected_domain
