from odoo.addons.component.core import Component


class Contract(Component):
    _name = "contract.listener"
    _inherit = "base.event.listener"
    _apply_on = ["contract.contract"]

    def on_record_write(self, record, fields=None):
        if "is_terminated" in fields and record.is_terminated:
            if record.is_pack and record.terminate_reason_id.id not in [
                self.env.ref("somconnexio.reason_location_change_from_SC_to_SC").id,
                self.env.ref("somconnexio.reason_holder_change_pack").id,
            ]:
                record.break_packs()
