from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CRMLeadRemesaWizard(models.TransientModel):
    _name = "crm.lead.remesa.wizard"
    crm_lead_ids = fields.Many2many("crm.lead")
    errors = fields.Char(string="Errors in remesa")

    def button_remesa(self):
        for lead in self.crm_lead_ids:
            lead.action_set_remesa()
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        crm_lead_ids = self.env.context["active_ids"]
        defaults["crm_lead_ids"] = crm_lead_ids
        errors = self._validate_crm_lines(crm_lead_ids)
        if errors:
            defaults["errors"] = _(
                "The next CRMLeadLines have a phone number that already exists in another contract/CRMLead: {}"  # noqa
            ).format(" ".join([str(id) for id in errors]).strip())
        return defaults

    def _validate_crm_lines(self, crm_lead_ids):
        errors = []
        crm_leads = self.env["crm.lead"].browse(crm_lead_ids)
        for crm_lead in crm_leads:
            try:
                crm_lead.validate_remesa()
            except ValidationError as error:
                if (
                    _(
                        "Contract or validated CRMLead with the same phone already exists."  # noqa
                    )
                    in error.args[0]
                ):
                    errors.append(crm_lead.id)
                else:
                    raise error
        if errors:
            return errors
