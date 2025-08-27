from odoo import fields, models


class ContractTerminateUserReason(models.Model):
    _name = "contract.terminate.user.reason"
    _description = "Contract Termination User Reason"
    _order = "sequence"

    name = fields.Char(required=True)
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Sequence")
    code = fields.Char(string="Code")
    terminate_user_comment_required = fields.Boolean(
        string="Comment required",
        default=False,
        help="If true, the user must provide a comment when terminating the contract",  # noqa
    )
