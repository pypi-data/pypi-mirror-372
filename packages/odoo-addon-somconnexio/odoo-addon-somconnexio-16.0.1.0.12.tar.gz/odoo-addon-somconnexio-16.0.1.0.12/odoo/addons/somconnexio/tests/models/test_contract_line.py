from datetime import date, timedelta

from ..sc_test_case import SCTestCase


class ContratLineTest(SCTestCase):
    def test_is_mobile_tariff(self):
        cl_data = {
            "name": "Test",
            "date_start": date.today() - timedelta(days=2),
            "recurring_invoicing_type": "post-paid",
        }

        # Broadband product
        ba_cl = self.browse_ref("somconnexio.contract_line_adsl")
        self.assertFalse(ba_cl.is_mobile_tariff_service)

        # Mobile service product
        mbl_service_cl = self.browse_ref("somconnexio.contract_line_mobile_il_20")
        self.assertTrue(mbl_service_cl.is_mobile_tariff_service)

        # Mobile one shot product
        cl_data["product_id"] = self.env.ref("somconnexio.DadesAddicionals1GB").id
        cl_data["contract_id"] = mbl_service_cl.contract_id.id
        mbl_one_shot_cl = self.env["contract.line"].create(cl_data)
        self.assertFalse(mbl_one_shot_cl.is_mobile_tariff_service)

        # Mobile additional service product
        cl_data["product_id"] = self.env.ref("somconnexio.EnviamentSIM").id
        cl_data["contract_id"] = mbl_service_cl.contract_id.id
        mbl_sim_cl = self.env["contract.line"].create(cl_data)
        self.assertFalse(mbl_sim_cl.is_mobile_tariff_service)
