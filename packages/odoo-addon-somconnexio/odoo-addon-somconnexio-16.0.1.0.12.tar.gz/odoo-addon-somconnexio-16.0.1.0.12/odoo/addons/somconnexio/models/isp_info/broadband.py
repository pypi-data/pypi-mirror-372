from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BroadbandISPInfo(models.Model):
    _inherit = "base.isp.info"

    _name = "broadband.isp.info"
    _description = "Broadband ISP Info"

    service_full_street = fields.Char(
        compute="_compute_service_full_street", store=True
    )
    service_street = fields.Char(string="Service Street")
    service_street2 = fields.Char(string="Service Street 2")
    service_zip_code = fields.Char(string="Service ZIP")
    service_city = fields.Char(string="Service City")
    service_state_id = fields.Many2one("res.country.state", string="Service State")
    service_country_id = fields.Many2one("res.country", string="Service Country")

    previous_service = fields.Selection(
        selection=[("fiber", "Fiber"), ("adsl", "ADSL"), ("4G", "4G")],
        string="Previous Service",
    )

    keep_phone_number = fields.Boolean(string="Keep Phone Number")
    no_previous_phone_number = fields.Boolean(
        string="Portability without previous phone number", default=False
    )

    service_supplier_id = fields.Many2one("service.supplier", string="Service Supplier")
    # Change Address attributes
    previous_contract_pon = fields.Char(string="previous_contract_pon")
    previous_contract_fiber_speed = fields.Char(string="previous_contract_fiber_speed")
    previous_contract_address = fields.Char(string="previous_contract_address")
    previous_contract_phone = fields.Char(string="previous_contract_phone")
    phone_number = fields.Char(default="-")
    previous_phone_number = fields.Char(
        string="Phone number before changing to a product without fix"
    )
    mobile_pack_contracts = fields.Many2many(
        "contract.contract", string="Related mobile contracts in pack"
    )

    @api.depends("service_street", "service_street2")
    def _compute_service_full_street(self):
        for record in self:
            if record.service_street2:
                record.service_full_street = "{} {}".format(
                    record.service_street, record.service_street2
                )
            else:
                record.service_full_street = record.service_street

    @api.constrains("type", "previous_provider")
    def _check_broadband_portability_info(self):
        if not self.type == "portability":
            return True
        if self.keep_phone_number and not self.phone_number:
            raise ValidationError(
                _("Phone number is required in a portability when keep the number")
            )
        if not self.previous_provider.broadband:
            raise ValidationError(
                _("This previous provider does not offer broadband services")
            )
