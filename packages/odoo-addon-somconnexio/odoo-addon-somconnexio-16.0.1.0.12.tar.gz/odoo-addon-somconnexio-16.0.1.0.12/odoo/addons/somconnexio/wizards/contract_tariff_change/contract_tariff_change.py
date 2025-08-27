from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ContractTariffChangeWizard(models.TransientModel):
    _name = "contract.tariff.change.wizard"
    contract_id = fields.Many2one("contract.contract")
    summary = fields.Char(required=True)
    done = fields.Boolean(default=True)
    location = fields.Char()
    note = fields.Char()

    product_category_id = fields.Many2one(
        related="contract_id.service_technology_id.service_product_category_id",
    )
    start_date = fields.Date("Start Date")

    current_tariff_contract_line = fields.Many2one(
        "contract.line",
        related="contract_id.current_tariff_contract_line",
    )

    current_tariff_product = fields.Many2one(
        "product.product",
        related="current_tariff_contract_line.product_id",
        string="Current Tariff",
    )

    new_tariff_product_id = fields.Many2one(
        "product.product",
        string="New tariff",
    )

    service_contract_type = fields.Char(
        "contract.contract",
        related="contract_id.service_contract_type",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["contract_id"] = self.env.context["active_id"]
        return defaults

    @api.onchange("new_tariff_product_id")
    def onchange_new_tariff_product_id(self):
        if self.new_tariff_product_id:
            self.summary = " ".join(
                [_("Tariff change"), self.new_tariff_product_id.showed_name]
            )

    @api.depends("contract_id")
    def _compute_will_force_other_mobiles_to_quit_pack(self):
        self.will_force_other_mobiles_to_quit_pack = (
            len(self.contract_id.contracts_in_pack) == 2
        )

    def button_change(self):
        self.ensure_one()

        if not self.start_date:
            raise ValidationError(_("Start date required"))

        available_relations = self.env["product.category.technology.supplier"].search(
            [
                (
                    "service_technology_id",
                    "=",
                    self.contract_id.service_technology_id.id,
                ),
                ("service_supplier_id", "=", self.contract_id.service_supplier_id.id),
            ]
        )
        available_categories = [c.product_category_id.id for c in available_relations]
        available_products_categ = self.env["product.template"].search(
            [("categ_id", "in", available_categories)]
        )
        if self.new_tariff_product_id.product_tmpl_id not in available_products_categ:
            raise ValidationError(
                _("Neither Service Technology nor Service Supplier cannot be changed")
            )

        new_tariff_line_dct = {
            "name": self.new_tariff_product_id.name,
            "product_id": self.new_tariff_product_id.id,
            "date_start": self.start_date,
            "contract_id": self.contract_id.id,
            "recurring_invoicing_type": self.contract_id.recurring_invoicing_type,
            "recurring_next_date": self.start_date + timedelta(days=1),
        }
        new_tariff_line = self.env["contract.line"].create(new_tariff_line_dct)

        if (
            self.current_tariff_contract_line
            and not self.current_tariff_contract_line.date_end
        ):  # No pending changes in future
            date_to_end = self.start_date - timedelta(days=1)
            self.current_tariff_contract_line.stop(date_end=date_to_end)
        else:  # Pending changes in future
            contract_line_to_end = (
                self.contract_id.contract_line_ids.filtered(
                    lambda line: line.is_mobile_tariff_service
                    and not line.date_end
                    and line.date_start >= date.today()
                )
                - new_tariff_line
            )
            date_to_end = contract_line_to_end.date_start
            contract_line_to_end.stop(date_end=date_to_end)

            if (
                self.current_tariff_contract_line
                and self.current_tariff_contract_line.date_end
                and self.current_tariff_contract_line.date_end > self.start_date
            ):  # New change before last pending change
                self.current_tariff_contract_line.stop(
                    date_end=self.start_date - timedelta(days=1)
                )

        message = _(
            "Contract tariff to be changed from '{}' to '{}' with start_date: {}"
        )
        self.contract_id.message_post(
            message.format(
                self.current_tariff_contract_line.product_id.showed_name,
                self.new_tariff_product_id.showed_name,
                self.start_date,
            )
        )

        if (
            self.contract_id.is_pack
            and self.new_tariff_product_id.product_tmpl_id.categ_id
            == self.env.ref("somconnexio.mobile_service")
            and not self.new_tariff_product_id.product_is_pack_exclusive
        ):
            message = _(
                "Pack broken because of mobile tariff change. Old linked fiber contract ref: '{}'"  # noqa
            )
            self.contract_id.message_post(
                message.format(self.contract_id.parent_pack_contract_id.code)
            )
            self.contract_id.break_packs()

        # Change from sharing data tariffs to pack/pinya (both pack exclusive)
        elif (
            self.contract_id.shared_bond_id
            and not self.new_tariff_product_id.has_sharing_data_bond
        ):
            message = _(
                "Stopped sharing data because of mobile tariff change. Old shared bond id: '{}'"  # noqa
            )
            self.contract_id.message_post(
                message.format(self.contract_id.shared_bond_id)
            )
            self.contract_id.quit_pack_and_update_mobile_tariffs()

        self._create_activity()
        return True

    def _create_activity(self):
        self.env["mail.activity"].create(
            {
                "summary": self.summary,
                "res_id": self.contract_id.id,
                "res_model_id": self.env.ref("contract.model_contract_contract").id,
                "user_id": self.env.user.id,
                "activity_type_id": self.env.ref(
                    "somconnexio.mail_activity_type_tariff_change"
                ).id,
                "done": self.done,
                "date_done": date.today(),
                "date_deadline": date.today(),
                "location": self.location,
                "note": self.note,
            }
        )
