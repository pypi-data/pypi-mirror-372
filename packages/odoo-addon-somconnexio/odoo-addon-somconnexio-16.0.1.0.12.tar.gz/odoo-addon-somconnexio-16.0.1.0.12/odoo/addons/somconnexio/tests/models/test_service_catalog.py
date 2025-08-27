from ..sc_test_case import SCTestCase


class TestServiceCatalog(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

    def test_products_availables_from_product_not_available_products(self):
        product = self.browse_ref("somconnexio.TrucadesIllimitades50GB")

        catalog = self.env["catalog.service"].products_availables_from_product(
            product.default_code
        )

        self.assertFalse(catalog)

    def test_products_availables_from_product_ok(self):
        expected_product = self.browse_ref("somconnexio.SenseFixFibra100Mb")
        product = self.browse_ref("somconnexio.Fibra100Mb")

        products = self.env["catalog.service"].products_availables_from_product(
            product.default_code
        )

        self.assertIn(expected_product, products)

    def test_pack_products(self):
        pack_product = self.browse_ref("somconnexio.PackFibra100MbIL20GB")
        pack_product.public = True
        not_pack_product = self.browse_ref("somconnexio.Fibra100Mb")
        not_pack_product.public = True

        products = self.env["catalog.service"].pack_products()

        self.assertIn(pack_product, products)
        self.assertNotIn(not_pack_product, products)

    def test_filter_not_contract_as_new_service(self):
        fiber_product = self.browse_ref("somconnexio.Fibra600Mb")
        fiber_product.contract_as_new_service = True
        products = self.env["catalog.service"].service_products()

        self.assertTrue(fiber_product.contract_as_new_service)
        self.assertIn(fiber_product, products)

        fiber_product.contract_as_new_service = False
        products = self.env["catalog.service"].service_products()

        self.assertFalse(fiber_product.contract_as_new_service)
        self.assertNotIn(fiber_product, products)
