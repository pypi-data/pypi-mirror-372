from odoo import api, fields, models


class ContractContractTerminate(models.TransientModel):
    _inherit = "contract.contract.terminate"

    terminate_user_reason_id = fields.Many2one(
        comodel_name="contract.terminate.user.reason",
        string="Termination User Reason",
        required=True,
        ondelete="cascade",
    )

    will_force_other_mobiles_to_quit_pack = fields.Boolean(
        compute="_compute_will_force_other_mobiles_to_quit_pack"
    )

    def terminate_contract(self):
        for wizard in self:
            wizard.contract_id.terminate_contract(
                wizard.terminate_reason_id,
                wizard.terminate_comment,
                wizard.terminate_date,
                wizard.terminate_user_reason_id,
            )
        return True

    @api.depends("contract_id")
    def _compute_will_force_other_mobiles_to_quit_pack(self):
        for wizard in self:
            contract = wizard.contract_id
            if contract.is_fiber:
                wizard.will_force_other_mobiles_to_quit_pack = bool(
                    contract.children_pack_contract_ids
                )
            elif contract.is_mobile:
                mbl_contracts_in_pack = contract.contracts_in_pack.filtered(
                    lambda c: c.is_mobile
                )
                wizard.will_force_other_mobiles_to_quit_pack = (
                    len(mbl_contracts_in_pack) == 2
                )
            else:
                wizard.will_force_other_mobiles_to_quit_pack = False
