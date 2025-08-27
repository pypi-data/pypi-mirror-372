from ..sc_test_case import SCTestCase
from mock import patch


class TestProductProduct(SCTestCase):
    def test_product_wo_catalog_name(self):
        product = self.browse_ref("somconnexio.Fibra100Mb")
        self.assertFalse(product.get_catalog_name("Min"))

    def test_product_catalog_name_in_product(self):
        product = self.browse_ref("somconnexio.SenseMinutsSenseDades")
        self.assertEqual(product.get_catalog_name("Data"), "0")
        self.assertEqual(product.get_catalog_name("Min"), "0")

    def test_product_default_attributes(self):
        product = self.browse_ref("somconnexio.Fibra100Mb")
        self.assertFalse(product.without_fix)
        self.assertTrue(product.contract_as_new_service)

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_write(self, message_post_mock):
        product = self.browse_ref("somconnexio.Fibra100Mb")
        old_value = product.default_code
        product.write({"default_code": "new-default-code-value"})
        expected_msg = "Field '{}' edited from '{}' to '{}'".format(
            "default_code", old_value, "new-default-code-value"
        )
        message_post_mock.assert_called_once_with(body=expected_msg)

    def test_get_offer_product_w_offer(self):
        product_with_offer = self.browse_ref("somconnexio.TrucadesIllimitades20GB")
        offer_product = self.browse_ref("somconnexio.TrucadesIllimitades20GBPack")

        self.assertEqual(product_with_offer.get_offer(), offer_product)

    def test_get_offer_sharing_product(self):
        sharing_data_product = self.browse_ref("somconnexio.50GBCompartides2mobils")

        self.assertFalse(sharing_data_product.get_offer())

    def test_get_offer_do_not_get_sharing_product_or_company(self):
        product_wo_offer = self.browse_ref("somconnexio.TrucadesIllimitades50GB")

        self.assertFalse(product_wo_offer.get_offer())

    def test_get_variant_with_attributes(self):
        sharing_3_mobiles_product = self.env.ref(
            "somconnexio.50GBCompartides3mobilsEiE"
        )
        sharing_2_mobiles_product = self.env.ref(
            "somconnexio.50GBCompartides2mobilsEiE"
        )

        attr_to_exclude = self.env.ref("somconnexio.Pack3Mobiles")
        attr_to_include = self.env.ref("somconnexio.Pack2Mobiles")

        new_product = sharing_3_mobiles_product.get_variant_with_attributes(
            attr_to_exclude, attr_to_include
        )

        self.assertEqual(new_product, sharing_2_mobiles_product)

    def test_get_variant_with_attributes_not_found(self):
        sharing_3_mobiles_product = self.env.ref(
            "somconnexio.150GBCompartides3mobilsEiE"
        )
        attr_to_exclude = self.env.ref("somconnexio.Pack3Mobiles") + self.env.ref(
            "somconnexio.Pack2Mobiles"
        )

        new_product = sharing_3_mobiles_product.get_variant_with_attributes(
            attr_to_exclude=attr_to_exclude
        )

        self.assertFalse(new_product)

    def test_get_technology(self):
        expected_technology = self.env.ref("somconnexio.service_technology_mobile")
        product = self.browse_ref("somconnexio.SenseMinutsSenseDades")
        self.assertEqual(
            product.product_tmpl_id.categ_id,
            expected_technology.service_product_category_id,
        )
        self.assertEqual(product.get_technology(), expected_technology)
