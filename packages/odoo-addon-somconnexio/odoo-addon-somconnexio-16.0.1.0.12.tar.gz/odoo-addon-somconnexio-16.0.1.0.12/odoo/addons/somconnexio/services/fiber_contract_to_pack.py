from odoo import _, models
from odoo.exceptions import MissingError


class FiberContractToPackService(models.AbstractModel):
    _name = "fiber.contract.to.pack.service"
    _register = True

    # pylint: disable=W8106
    def create(self, **params):
        """
        Returns all contracts from the requested that match these
        conditions:
        - Own by requested partner (ref)
        - Supplier MM
        - Technology fiber
        - Not in pack (if not mobiles_sharing_data)
        """
        partner_ref = params.get("partner_ref")

        partner = (
            self.env["res.partner"]
            .sudo()
            .search([("parent_id", "=", False), ("ref", "=", partner_ref)])
        )

        if not partner:
            raise MissingError(_("Partner with ref {} not found").format(partner_ref))

        contracts = (
            self.env["contract.contract"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", partner.id),
                    ("is_terminated", "=", False),
                    (
                        "service_technology_id",
                        "=",
                        self.env.ref("somconnexio.service_technology_fiber").id,
                    ),
                ]
            )
        )
        # If the flag mobile_sharing_data is True,
        # only return the fiber contracts without mobile
        # related or with only one mobile related
        if params.get("all") == "true":
            pass
        elif params.get("mobiles_sharing_data") == "true":
            contracts = contracts.filtered(
                lambda c: len(c.children_pack_contract_ids) == 1
                or not c.children_pack_contract_ids
            )
        else:
            contracts = contracts.filtered(lambda c: not c.children_pack_contract_ids)

        contracts = self._filter_already_used_contracts(contracts)

        if not contracts:
            raise MissingError(
                _("No fiber contracts available to pack found with this user")
            )

        return contracts

    def _filter_already_used_contracts(self, contracts):
        contracts = self._filter_out_fibers_used_in_ODOO_lead_lines(contracts)
        return contracts

    def _filter_out_fibers_used_in_ODOO_lead_lines(self, contracts):
        """
        From a list of fiber contracts, search if any of them is
        already referenced in a mobile provisioning crm lead line
        (field `linked_fiber_contract_id`).
        If so, that fiber contract is about to be linked to a mobile
        offer, and shouldn't be available for others.
        Returns the original contract list excluding, if found,
        those linked in mobile lead lines.
        """

        if not contracts:
            return []

        stages_to_discard = [
            self.env.ref("crm.stage_lead4").id,
            self.env.ref("somconnexio.stage_lead5").id,
        ]
        partner_id = contracts[0].partner_id.id
        mbl_lead_lines = self.env["crm.lead.line"].search(
            [
                ("partner_id", "=", partner_id),
                ("mobile_isp_info", "!=", False),
                ("stage_id", "not in", stages_to_discard),
            ]
        )

        already_linked_contracts = mbl_lead_lines.mapped("mobile_isp_info").mapped(
            "linked_fiber_contract_id"
        )

        return contracts - already_linked_contracts
