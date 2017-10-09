# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'res_partner': [
        ('birthdate', None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
    cr.execute(
        # we rely on the ORM to write this value
        'alter table ir_model_fields add column store boolean'
    )
    openupgrade.copy_columns(cr, {
        'ir_act_window': [
            ('target', None, None),
        ],
    })
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('target'), 'target',
        [
            ('inlineview', 'inline'),
        ],
        table='ir_act_window')
    cr.execute(
        "update ir_ui_view set type='kanban' where type='sales_team_dashboard'"
    )
    cr.execute('update res_currency set symbol=name where symbol is null')
    # create xmlids for installed languages
    cr.execute(
        '''insert into ir_model_data
        (module, name, model, res_id)
        select
        'base',
        'lang_' ||
        case
            when char_length(code) > 2 then
            case
                when upper(substring(code from 1 for 2)) =
                upper(substring(code from 4 for 2)) then
                    substring(code from 1 for 2)
                else
                    code
            end
            else
                code
        end,
        'res.lang', id
        from res_lang''')
    openupgrade.update_module_names(
        cr, [
            ('account_full_reconcile', 'account'),
            ('mail_tip', 'mail'),
            ('project_timesheet', 'hr_timesheet'),
            ('sale_service', 'sale_timesheet'),
            ('share', 'base'),
            ('web_tip', 'web'),
            ('web_view_editor', 'web'),
            ('mail_tip', 'mail'),
            ('im_odoo_support', 'im_livechat'),
            ('marketing', 'marketing_campaign'),
            # OCA/account-invoicing
            ('purchase_stock_picking_return_invoicing_open_qty',
             'purchase_stock_picking_return_invoicing'),
            # OCA/e-commerce
            ('website_sale_b2c', 'sale'),  # used groups are in sale
            # OCA/sale-workflow
            ('sale_order_back2draft', 'sale'),
            # OCA/social
            ('mass_mailing_security_group', 'mass_mailing'),
        ], merge_modules=True,
    )

    # Modificado por TRESCLOUD, mapeo de modulos
    openupgrade.update_module_names(
        cr, [
            ('account_analytic_plans_simplified','l10n_ec'),
            ('account_chart','l10n_ec'),
            ('account_invoice_fiscal_position_update','l10n_ec'),
            ('account_move_line_allow_update','l10n_ec'),
            ('account_move_line_group_analytic','l10n_ec'),
            ('account_move_line_report','l10n_ec'),
            ('account_move_line_report_xls','l10n_ec'),
            ('account_payment_order','l10n_ec'),
            ('account_report_company','l10n_ec'),
            ('analytic_contract_hr_expense','l10n_ec'),
            ('analytic_user_function','l10n_ec'),
            ('asset','l10n_ec'),
            ('authorization_for_pricelist','l10n_ec'),
            ('base_partner_merge','l10n_ec'),
            ('base_status','l10n_ec'),
            ('BizzAppDev-oerp_no_phoning_home','l10n_ec'),
            ('contract','l10n_ec'),
            ('crm_default_sales_team','l10n_ec'),
            ('crm_todo','l10n_ec'),
            ('ecua_2015_tax','l10n_ec'),
            ('ecua_account_reconciliation_enhancements','l10n_ec'),
            ('ecua_ats_report','l10n_ec'),
            ('ecua_cities','l10n_ec'),
            ('ecua_sri_refund','ecua_refund'),
            ('ecua_tax','l10n_ec'),
            ('edi','l10n_ec'),
            ('fdu_motd','l10n_ec'),
            ('google_base_account','l10n_ec'),
            ('google_docs','l10n_ec'),
            ('hr_applicant_document','l10n_ec'),
            ('hr_attendance_improved_report','l10n_ec'),
            ('hr_extra_input_output','l10n_ec'),
            ('hr_third_party_payments','l10n_ec'),
            ('hr_timesheet_invoice','l10n_ec'),
            ('knowledge','l10n_ec'),
            ('l10n_ec_niif_minimal','l10n_ec'),
            ('law_of_solidarity','l10n_ec'),
            ('npg_bank_account_reconciliation','l10n_ec'),
            ('picking_user','l10n_ec'),
            ('popup_reminder','l10n_ec'),
            ('portal_crm','l10n_ec'),
            ('portal_event','l10n_ec'),
            ('portal_hr_employees','l10n_ec'),
            ('portal_project','l10n_ec'),
            ('portal_project_issue','l10n_ec'),
            ('process','l10n_ec'),
            ('product_purchase_history','l10n_ec'),
            ('product_serial','l10n_ec'),
            ('project_advance_reports','l10n_ec'),
            ('project_gtd','l10n_ec'),
            ('report_aeroo','l10n_ec'),
            ('report_aeroo_ooo','l10n_ec'),
            ('report_webkit','l10n_ec'),
            ('sale_ingredients','l10n_ec'),
            ('sale_pricelist_recalculation','l10n_ec'),
            ('sale_validity_term','l10n_ec'),
            ('stock_analytic','l10n_ec'),
            ('stock_delivery_date','l10n_ec'),
            ('stock_picking_invoice_link','l10n_ec'),
            ('stock_product_moves','l10n_ec'),
            ('trescloud_erpdeuna','l10n_ec'),
            ('trescloud_filter_partner','l10n_ec'),
            ('trescloud_financial_control_of_projects','l10n_ec'),
            ('trescloud_fleet','l10n_ec'),
            ('trescloud_graphic','l10n_ec'),
            ('trescloud_remove_reports_default','l10n_ec'),
            ('trescloud_reportes_generales','l10n_ec'),
            ('trescloud_retail_report','l10n_ec'),
            ('trescloud_setec_password','l10n_ec'),
            ('trescloud_show_popup_reminder','l10n_ec'),
            ('trescloud_support_sheet','l10n_ec'),
            ('vat_tax_fourteen_percent','l10n_ec'),
            ('warning','l10n_ec'),
            ('web_m2x_options_extra_lock','l10n_ec'),
            ('web_pdf_preview','l10n_ec'),
            ('web_printscreen_zb','l10n_ec'),
            ('web_shortcuts','l10n_ec'),
        ], merge_modules=True,
    )
