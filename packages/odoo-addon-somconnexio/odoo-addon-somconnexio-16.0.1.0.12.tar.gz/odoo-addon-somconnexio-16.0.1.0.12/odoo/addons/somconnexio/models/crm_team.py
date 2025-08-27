from odoo import models, api, fields


class CrmTeam(models.Model):
    _inherit = "crm.team"
    _description = "Sales Team"

    code = fields.Char(
        string="Code", required=True, help="Unique code to identify the crm team."
    )

    _sql_constraints = [
        ('code', 'unique(code)', 'The code of the crm team must be unique !'),
    ]

    @api.model
    def _get_default_team_id(self, user_id=None, domain=None):
        """
        Overrides 'sales_team' module method which sets a team_id
        by user and membership regardless of the team_id input param,
        which is also set as default_team_id in the context.
        """
        return self.env["crm.team"].browse(self.env.context.get("default_team_id"))
