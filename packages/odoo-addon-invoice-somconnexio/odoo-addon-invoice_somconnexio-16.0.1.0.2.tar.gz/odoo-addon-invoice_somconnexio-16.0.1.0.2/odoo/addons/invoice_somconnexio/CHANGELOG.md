# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [16.0.1.0.2] - 2025-08-26
### Fixed
- [#1571](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1571) Replace state by payment_state in to_dict account_invoice_service

## [16.0.1.0.1] - 2025-06-18
### Fixed
- [#1528](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1528) Use the partner bank id of the invoice reverted

## [16.0.1.0.0] - 2025-04-09
### Changed
- Updated content_disposition import path
- Replaced fields_get with _fields
- Updated invoice state handling (open → posted)
- Fixed payment_mode_type computation
- Improved last_return_amount computation
- Added move_type to invoice creation
- Updated tax_ids command format
- Used f-strings instead of format()
- Added company_id to views to support multi-company
- Replaced invoice_id with move_id in account_invoice_line
- Updated AbstractModel imports to use models.AbstractModel
- Updated env.user.company_id to env.company
- Fixed payment_return to map move_id instead of invoice_id
- Added _description to models
- Added required dependencies to manifest (account_payment_partner, account_payment_order)
- Improved send_tokenized_invoice model
- Moved groups_id from view to groups attribute in page element
- Renamed view IDs to follow naming conventions
- Removed unnecessary <data> tags from XML files
- Fixed syntax in account_invoice_confirm with proper list notation
- Updated type to move_type in invoice confirmation wizards
- Added view_mode to act_window actions
- Improved XML formatting for better readability
- Changed btn-secondary to btn-default for cancel buttons
- Updated contract_invoice_payment and invoice_claim_1_send wizards
- Added _description to all TransientModel classes
- Fixed send_mail target (invoice.id instead of partner_id)
- Added css classes to all buttons for consistency
- Removed deprecated view_type parameter
- Updated payment order wizards to use binding_model_id instead of binding_model
- Enhanced button texts for payment order actions (Create → Confirm)
- Added binding_view_types to specify where actions should appear

## [12.0.1.0.2] - 2025-02-11
### Fixed
- [#1352](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1352) Adapted the Payment Order purpose value with the new customer invoice journal

## [12.0.1.0.1] - 2025-01-22
### Added
- [#1336](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1336) Add journal_id to confirm invoices between dates wizard

### Fixed
- [#1335](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1335) Notify invoice number listener filter
- [#1339](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1339) Add locale to the download invoice URL
- [#1340](https://git.coopdevs.org/coopdevs/som-connexio/odoo/odoo-somconnexio/-/merge_requests/1340) search_count to return totalNumberOfRecords in account_invoice_service

## [12.0.1.0.0] - 2025-01-08
### Added
- [#1196](https://git.coopdevs.org/coopdevs/som-connexio/odoo-somconnexio/-/merge_requests/1196) Add invoice_somconnexio module.
