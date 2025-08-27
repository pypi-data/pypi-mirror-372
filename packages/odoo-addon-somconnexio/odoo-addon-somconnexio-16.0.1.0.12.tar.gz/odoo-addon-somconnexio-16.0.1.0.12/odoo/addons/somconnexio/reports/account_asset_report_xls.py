import logging

from odoo import models, _
from odoo.exceptions import UserError

from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


IR_TRANSLATION_NAME = "account.asset.report"


class AssetReportXlsx(models.AbstractModel):
    _inherit = "report.account_asset_management.asset_report_xls"

    def _get_asset_template(self):
        asset_template = {
            "account": {
                "header": {
                    "type": "string",
                    "value": self._("Account"),
                },
                "asset": {
                    "type": "string",
                    "value": self._render("asset.profile_id.account_asset_id.code"),
                },
                "width": 20,
            },
            "name": {
                "header": {
                    "type": "string",
                    "value": self._("Name"),
                },
                "asset_group": {
                    "type": "string",
                    "value": self._render("group.name or ''"),
                },
                "asset": {
                    "type": "string",
                    "value": self._render("asset.name"),
                },
                "width": 40,
            },
            "code": {
                "header": {
                    "type": "string",
                    "value": self._("Reference"),
                },
                "asset_group": {
                    "type": "string",
                    "value": self._render("group.code or ''"),
                },
                "asset": {
                    "type": "string",
                    "value": self._render("asset.code or ''"),
                },
                "width": 20,
            },
            "date_start": {
                "header": {
                    "type": "string",
                    "value": self._("Asset Start Date"),
                },
                "asset": {
                    "value": self._render("asset.date_start"),
                    "format": self.format_tcell_date_left,
                },
                "width": 20,
            },
            "date_end": {
                "header": {
                    "type": "string",
                    "value": self._("Asset End Date"),
                },
                "asset": {
                    "value": self._render("period_end_date"),
                    "format": self.format_tcell_date_left,
                },
                "width": 20,
            },
            "date_remove": {
                "header": {
                    "type": "string",
                    "value": self._("Asset Removal Date"),
                },
                "asset": {
                    "value": self._render("asset.date_remove"),
                    "format": self.format_tcell_date_left,
                },
                "width": 20,
            },
            "depreciation_base": {
                "header": {
                    "type": "string",
                    "value": self._("Depreciation Base"),
                    "format": self.format_theader_yellow_right,
                },
                "asset_group": {
                    "type": "number",
                    "value": self._render("group._depreciation_base"),
                    "format": self.format_theader_blue_amount_right,
                },
                "asset": {
                    "type": "number",
                    "value": self._render("asset.depreciation_base"),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
            "salvage_value": {
                "header": {
                    "type": "string",
                    "value": self._("Salvage Value"),
                    "format": self.format_theader_yellow_right,
                },
                "asset_group": {
                    "type": "number",
                    "value": self._render("group._salvage_value"),
                    "format": self.format_theader_blue_amount_right,
                },
                "asset": {
                    "type": "number",
                    "value": self._render("asset.salvage_value"),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
            "period_start_value": {
                "header": {
                    "type": "string",
                    "value": self._("Period Start Value"),
                    "format": self.format_theader_yellow_right,
                },
                "asset_group": {
                    "type": "number",
                    "value": self._render("group._period_start_value"),
                    "format": self.format_theader_blue_amount_right,
                },
                "asset": {
                    "type": "number",
                    "value": self._render("asset._period_start_value"),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
            "period_depr": {
                "header": {
                    "type": "string",
                    "value": self._("Period Depreciation"),
                    "format": self.format_theader_yellow_right,
                },
                "asset_group": {
                    "type": "number",
                    "value": self._render(
                        "group._period_start_value-group._period_end_value"
                    ),
                    "format": self.format_theader_blue_amount_right,
                },
                "asset": {
                    "type": "number",
                    "value": self._render(
                        "asset._period_start_value-asset._period_end_value"
                    ),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
            "period_end_value": {
                "header": {
                    "type": "string",
                    "value": self._("Period End Value"),
                    "format": self.format_theader_yellow_right,
                },
                "asset_group": {
                    "type": "number",
                    "value": self._render("group._period_end_value"),
                    "format": self.format_theader_blue_amount_right,
                },
                "asset": {
                    "type": "number",
                    "value": self._render("asset._period_end_value"),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
            "period_end_depr": {
                "header": {
                    "type": "string",
                    "value": self._("Tot. Depreciation"),
                    "format": self.format_theader_yellow_right,
                },
                "asset_group": {
                    "type": "formula",
                    "value": self._render("total_depr_formula"),
                    "format": self.format_theader_blue_amount_right,
                },
                "asset": {
                    "type": "formula",
                    "value": self._render("total_depr_formula"),
                    "format": self.format_tcell_amount_right,
                },
                "width": 18,
            },
            "method": {
                "header": {
                    "type": "string",
                    "value": self._("Comput. Method"),
                    "format": self.format_theader_yellow_center,
                },
                "asset": {
                    "type": "string",
                    "value": self._render("asset.method or ''"),
                    "format": self.format_tcell_center,
                },
                "width": 20,
            },
            "method_number": {
                "header": {
                    "type": "string",
                    "value": self._("Number of Years"),
                    "format": self.format_theader_yellow_center,
                },
                "asset": {
                    "value": self._render("years"),
                    "format": self.format_tcell_integer_center,
                },
                "width": 20,
            },
            "perc_amort_anual": {
                "header": {
                    "type": "string",
                    "value": self._("% Amort Anual"),
                    "format": self.format_theader_yellow_center,
                },
                "asset": {
                    "value": self._render("perc_amort_anual"),
                    "format": self.format_tcell_percent_center,
                },
                "width": 20,
            },
            "prorata": {
                "header": {
                    "type": "string",
                    "value": self._("Prorata Temporis"),
                    "format": self.format_theader_yellow_center,
                },
                "asset": {
                    "type": "boolean",
                    "value": self._render("asset.prorata"),
                    "format": self.format_tcell_center,
                },
                "width": 20,
            },
            "state": {
                "header": {
                    "type": "string",
                    "value": self._("Status"),
                    "format": self.format_theader_yellow_center,
                },
                "asset": {
                    "type": "string",
                    "value": self._render("asset.state"),
                    "format": self.format_tcell_center,
                },
                "width": 8,
            },
        }
        asset_template.update(self.env["account.asset"]._xls_asset_template())

        return asset_template

    def _asset_report(self, workbook, ws, ws_params, data, wiz):
        report = ws_params["report_type"]

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers["standard"])
        ws.set_footer(self.xls_footers["standard"])

        wl = ws_params["wanted_list"]
        if "account" not in wl:
            raise UserError(
                _(
                    "The 'account' field is a mandatory entry of the "
                    "'_xls_%s_fields' list !"
                )
                % report
            )

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._report_title(ws, row_pos, ws_params, data, wiz)

        def asset_filter(asset):
            filter = getattr(self, "{}_filter".format(report))
            return filter(wiz, asset)

        assets = self._assets.filtered(asset_filter)

        if not assets:
            return self._empty_report(ws, row_pos, ws_params, data, wiz)

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="header",
            default_format=self.format_theader_yellow_left,
        )

        ws.freeze_panes(row_pos, 0)

        row_pos_start = row_pos
        depreciation_base_pos = "depreciation_base" in wl and wl.index(
            "depreciation_base"
        )
        salvage_value_pos = "salvage_value" in wl and wl.index("salvage_value")
        period_start_value_pos = "period_start_value" in wl and wl.index(
            "period_start_value"
        )
        period_end_value_pos = "period_end_value" in wl and wl.index("period_end_value")

        period_start_pos = "date_start" in wl and wl.index("date_start")
        perc_amort_anual_pos = "perc_amort_anual" in wl and wl.index("perc_amort_anual")

        entries = []
        root = wiz.asset_group_id
        root_val = self._grouped_assets[root]
        error_dict = {
            "no_table": self.env["account.asset"],
            "dups": self.env["account.asset"],
        }

        self._create_report_entries(ws_params, wiz, entries, root, root_val, error_dict)

        # traverse entries in reverse order to calc totals
        for i, entry in enumerate(reversed(entries)):
            group = entry.get("group")
            if "group" in entry:
                parent = group.parent_id
                for e in reversed(entries[: -i - 1]):
                    g = e.get("group")
                    if g == parent:
                        g._depreciation_base += group._depreciation_base
                        g._salvage_value += group._salvage_value
                        g._period_start_value += group._period_start_value
                        g._period_end_value += group._period_end_value
                        continue

        processed = []
        for entry in entries:
            period_start_date_cell = period_start_pos and self._rowcol_to_cell(
                row_pos, period_start_pos
            )
            perc_amort_anual_cell = perc_amort_anual_pos and self._rowcol_to_cell(
                row_pos, perc_amort_anual_pos
            )

            period_end_date_cell = ""
            if period_start_date_cell and perc_amort_anual_cell:
                period_end_date_cell = (
                    period_start_date_cell + "+365*1/" + perc_amort_anual_cell
                )

            period_start_value_cell = period_start_value_pos and self._rowcol_to_cell(
                row_pos, period_start_value_pos
            )
            period_end_value_cell = period_end_value_pos and self._rowcol_to_cell(
                row_pos, period_end_value_pos
            )
            depreciation_base_cell = depreciation_base_pos and self._rowcol_to_cell(
                row_pos, depreciation_base_pos
            )
            period_diff_formula = period_end_value_cell and (
                period_start_value_cell + "-" + period_end_value_cell
            )
            total_depr_formula = period_end_value_cell and (
                depreciation_base_cell + "-" + period_end_value_cell
            )

            if "group" in entry:
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="asset_group",
                    render_space={
                        "group": entry["group"],
                        "period_diff_formula": period_diff_formula,
                        "total_depr_formula": total_depr_formula,
                    },
                    default_format=self.format_theader_blue_left,
                )

            else:
                asset = entry["asset"]
                if asset in processed:
                    error_dict["dups"] += asset
                    continue
                else:
                    if asset.method_end:
                        period_end_date = asset.method_end
                        years = (
                            relativedelta(asset.method_end, asset.date_start).years
                            + relativedelta(asset.method_end, asset.date_start).months
                            / 12
                        )
                        if years == 0:
                            years = 1
                    else:
                        years = int(
                            asset.method_number
                            if asset.method_time == "year"
                            else 100 / asset.annual_percentage
                        )
                        period_end_date = asset.date_start + relativedelta(years=years)
                        processed.append(asset)

                    perc_amort_anual = 1 / years
                row_pos = self._write_line(
                    ws,
                    row_pos,
                    ws_params,
                    col_specs_section="asset",
                    render_space={
                        "asset": asset,
                        "period_diff_formula": period_diff_formula,
                        "total_depr_formula": total_depr_formula,
                        "period_end_date_cell": period_end_date_cell,
                        "period_end_date": period_end_date,
                        "years": years,
                        "perc_amort_anual": perc_amort_anual,
                    },
                    default_format=self.format_tcell_left,
                )
        asset_total_formula = depreciation_base_pos and self._rowcol_to_cell(
            row_pos_start, depreciation_base_pos
        )
        salvage_total_formula = salvage_value_pos and self._rowcol_to_cell(
            row_pos_start, salvage_value_pos
        )
        period_start_total_formula = period_start_value_pos and self._rowcol_to_cell(
            row_pos_start, period_start_value_pos
        )
        period_end_total_formula = period_end_value_pos and self._rowcol_to_cell(
            row_pos_start, period_end_value_pos
        )
        period_dif_total_formula = period_start_total_formula

        if period_start_total_formula and period_end_total_formula:
            period_dif_total_formula = (
                period_start_total_formula + "-" + period_end_total_formula
            )

        period_start_value_cell = period_start_value_pos and self._rowcol_to_cell(
            row_pos, period_start_value_pos
        )
        period_end_value_cell = period_end_value_pos and self._rowcol_to_cell(
            row_pos, period_end_value_pos
        )
        depreciation_base_cell = depreciation_base_pos and self._rowcol_to_cell(
            row_pos, depreciation_base_pos
        )
        period_diff_formula = period_end_value_cell and (
            period_start_value_cell + "-" + period_end_value_cell
        )
        total_depr_formula = period_end_value_cell and (
            depreciation_base_cell + "-" + period_end_value_cell
        )

        row_pos = self._write_line(
            ws,
            row_pos,
            ws_params,
            col_specs_section="totals",
            render_space={
                "asset_total_formula": asset_total_formula,
                "salvage_total_formula": salvage_total_formula,
                "period_start_total_formula": period_start_total_formula,
                "period_end_total_formula": period_end_total_formula,
                "period_diff_formula": period_diff_formula,
                "total_depr_formula": total_depr_formula,
                "period_dif_total_formula": period_dif_total_formula,
                "period_end_date_cell": period_end_date_cell,
            },
            default_format=self.format_theader_yellow_left,
        )

        for k in error_dict:
            if error_dict[k]:
                if k == "no_table":
                    reason = _("Missing depreciation table")
                elif k == "dups":
                    reason = _("Duplicate reporting entries")
                else:
                    reason = _("Undetermined error")
                row_pos += 1
                err_msg = _("Assets to be corrected") + ": "
                err_msg += "%s" % [x[1] for x in error_dict[k].name_get()]
                err_msg += " - " + _("Reason") + ": " + reason
                ws.write_string(row_pos, 0, err_msg, self.format_left_bold)
