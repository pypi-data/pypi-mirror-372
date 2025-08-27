# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [16.0.1.0.12] - 2025-08-26
### Fixed
- [#1573](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1573) Fix contract views
- [#1569](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1569) Fix mail compose _onchange_template_id
- [#1568](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1568) Archive old duplicated product templates

## [16.0.1.0.11] - 2025-07-27
### Added
- [#1570](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1570) Add account_move_line form view

## [16.0.1.0.10] - 2025-07-08
### Fixed
- [#1563](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1563) Remove cancel button from mail.Activity template

## [16.0.1.0.9] - 2025-07-04
### Added
- [#1558](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1558) No default activity_type_id when creating activities

### Fixed
- [#1542](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1542) Fix mail activity search filters active
- [#1552](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1552) Fix move lines without date_due

### Changed
- [#1556](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1556) Refactor create_lead_from_partner wizard

## [16.0.1.0.8] - 2025-06-26
### Fixed
- [#1555](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1555) Fix partner_bank_id in payments

## [16.0.1.0.7] - 2025-06-25
### Changed
- [#1405](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1405) Adaptation to new multimedia modules

## [16.0.1.0.6] - 2025-06-18
### Fixed
- [#1528](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1528) Use the partner bank id of the invoice reverted
- [#1529](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1529) Comunication in payment order with old invoices
- [#1535](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1535) Set no-update to product.template.attribute.line data
- [#1537](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1537) Hide done activities in chatter

## [16.0.1.0.5] - 2025-06-06
### Fixed
- [#1520](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1520) Add missing IL23 product
- [#1517](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1517) Fix compute current_tariff_contract_line

## [16.0.1.0.4] - 2025-06-03
### Fixed
- [#1505](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1505) Fix invoice claim templates

## [16.0.1.0.3] - 2025-05-30
### Fixed
- [#1506](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1506) Replace email_tags by show_email in context that show partner email
- [#1504](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1504) Compute mail activity count in partner

### Added
- [#1500](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1500) Add code field in crm team

### Removed
- [#1498](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1498) Remove unused buttons in mail activity view

## [16.0.1.0.2] - 2025-05-28
### Fixed
- [#1493](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1493) restore button actions mail activity
- [#1491](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1491) Fix cache error with create_lead_from_partner wizard

### Removed
- [#1490](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1490) Remove GRETA fiber products from code

## [16.0.1.0.1] - 2025-05-27
### Fixed
- [#1482](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1482) Use _run_action_mail_post_multi with _send_background_email
- [#1480](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1480) Use contract_one_shot_request wizard from contract view
- [#1479](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1479) Fix donor icc domain in create lead wizard view

## [16.0.1.0.0] - 2025-05-26
### Added
- Migrate somconnexio module to ODOO v16
