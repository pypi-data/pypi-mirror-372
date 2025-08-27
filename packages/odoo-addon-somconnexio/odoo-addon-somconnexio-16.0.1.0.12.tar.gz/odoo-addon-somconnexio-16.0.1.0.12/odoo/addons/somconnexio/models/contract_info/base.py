from odoo import _, fields, models


class BaseServiceContractInfo(models.AbstractModel):
    _name = "base.service.contract.info"
    _rec_name = "phone_number"
    phone_number = fields.Char("Phone Number", required=True)

    def write(self, values):
        for contract_info in self:
            for key in values:
                message = _("{} changed from {} to {}").format(
                    self._fields[key].string, self[key], values[key]
                )
                contract_info.contract_ids.message_post(message)
        super().write(values)
