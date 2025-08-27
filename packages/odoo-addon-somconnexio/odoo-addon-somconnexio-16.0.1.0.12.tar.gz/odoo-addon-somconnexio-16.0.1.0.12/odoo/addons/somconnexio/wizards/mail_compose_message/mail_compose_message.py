from odoo import api, models


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.onchange("template_id")
    def _onchange_template_id_wrapper(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        if self.model == "crm.lead":
            crm_lead = self.env["crm.lead"].browse(self.res_id)
            lang = crm_lead.partner_id.lang
            ctx.update(lang=lang)
        values = self.with_context(ctx)._onchange_template_id(
            self.template_id.id, self.composition_mode, self.model, self.res_id
        )["value"]
        for fname, value in values.items():
            setattr(self, fname, value)

    def render_message(self, res_ids):
        template_values = super().render_message(res_ids)
        if self.template_id:
            langs = self.env["mail.template"]._render_template(
                self.template_id.lang, self.model, res_ids
            )
            res_id_by_langs = {}
            for res_id in res_ids:
                if langs[res_id] not in res_id_by_langs:
                    res_id_by_langs[langs[res_id]] = []
                res_id_by_langs[langs[res_id]].append(res_id)
            bodies = {}
            subjects = {}
            for lang in res_id_by_langs:
                body_html_i18n = self.template_id.with_context(lang=lang).body_html
                subject_i18n = self.template_id.with_context(lang=lang).subject
                bodies.update(
                    self.env["mail.template"]._render_template(
                        body_html_i18n,
                        self.model,
                        res_id_by_langs[lang],
                        post_process=True,
                    )
                )
                subjects.update(
                    self.env["mail.template"]._render_template(
                        subject_i18n,
                        self.model,
                        res_id_by_langs[lang],
                        post_process=True,
                    )
                )
            for res_id in res_ids:
                template_values[res_id]["body"] = bodies[res_id]
                template_values[res_id]["subject"] = subjects[res_id]
        return template_values
