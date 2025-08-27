import unicodedata

from odoo import api, models


def normalize_string(input_str):
    # Normalize the input string to decompose combined characters
    input_str = input_str.replace(" ", "").replace("·", "")
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    # Filter out combining diacritical marks
    return "".join([char for char in nfkd_form if not unicodedata.combining(char)])


class IrModelData(models.TransientModel):
    _name = "somconnexio.module"

    @api.model
    def load_fiscal_location(self):
        account = self.env["account.account"].search([("code", "=", "12000017")])
        if account:
            return True

        # Remove the Tax repartition lines only for CI. Without this line, the
        # CI fails with the error raised by _unlink_except_linked_to_tax_repartition_line  # noqa
        self.env["account.tax.repartition.line"].search([]).unlink()

        chart_template_id = self.env.ref("somconnexio.account_chart_template_sc")
        company_id = self.env.ref("base.main_company")
        chart_template_id._load(company_id)

    @api.model
    def import_bank_data(self):
        bank_data_wizard = self.sudo().env["l10n.es.partner.import.wizard"].create({})
        bank_data_wizard.execute()

    @api.model
    def install_languages(self):
        lang_ids = self.env["res.lang"].search(
            [("active", "=", False), ("code", "in", ["es_ES", "ca_ES"])]
        )
        installer = (
            self.sudo().env["base.language.install"].create({"lang_ids": lang_ids})
        )
        installer.lang_install()

    @api.model
    def disable_company_noupdate(self):
        company_imd = self.env["ir.model.data"].search([("name", "=", "main_company")])
        company_imd.noupdate = False

    @api.model
    def clean_demo_data(self):
        self.env.cr.execute("DELETE FROM account_move_line")
        self.env.cr.execute("DELETE FROM account_move")
        self.env.cr.execute("DELETE FROM account_bank_statement")
        self.env.cr.execute("DELETE FROM sale_order")

    @api.model
    def disable_admin_noupdate(self):
        admin_imd = self.env["ir.model.data"].search(
            [
                ("name", "=", "user_admin"),
                ("module", "=", "base"),
            ]
        )
        admin_imd.noupdate = False

    @api.model
    def restore_admin_noupdate(self):
        admin_imd = self.env["ir.model.data"].search(
            [
                ("name", "=", "user_admin"),
                ("module", "=", "base"),
            ]
        )
        admin_imd.noupdate = True

    @api.model
    def disable_crm_lead_stages_noupdate(self):
        stages = self.env["ir.model.data"].search(
            [
                ("name", "in", ("stage_lead2", "stage_lead3", "stage_lead5")),
                ("module", "=", "crm"),
            ]
        )
        for stage in stages:
            stage.noupdate = False

    @api.model
    def restore_crm_lead_stages_noupdate(self):
        stages = self.env["ir.model.data"].search(
            [
                ("name", "in", ("stage_lead2", "stage_lead3", "stage_lead5")),
                ("module", "=", "crm"),
            ]
        )
        for stage in stages:
            stage.noupdate = True
