# -*- coding: utf-8 -*-
# Copyright 2015 Microcom
# Copyright 2016 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# Copyright 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# Copyright 2016 Opener B.V. - Stefan Rijnhart
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    # 'invoice_id' in 8.0 already referred to invoice lines
    'sale_order_line_invoice_rel': [
        ('invoice_id', 'invoice_line_id'),
    ],
}

field_renames = [
    ('sale.order', 'sale_order', 'section_id', 'team_id'),
    ('account.invoice', 'account_invoice', 'section_id', 'team_id'),
    ('sale.order.tax', 'sale_order_tax', 'order_line_id',
     'sale_order_line_id'),
    ('sale.order.tax', 'sale_order_tax', 'tax_id', 'account_tax_id'),
    # renamings with oldname attribute - They also need the rest of operations
    ('sale.order', 'sale_order', 'fiscal_position', 'fiscal_position_id'),
    ('sale.order', 'sale_order', 'payment_term', 'payment_term_id'),
    ('sale.order.line', 'sale_order_line', 'delay', 'customer_lead'),
]

table_renames = [
    ('sale_order_tax', 'account_tax_sale_order_line_rel'),
]

column_copies = {
    'sale_order': [
        ('state', None, None),
    ],
    'sale_order_line': [
        ('state', None, None),
    ],
}


def map_order_state(cr):
    """ Map values for state field in sale.order and sale.order.line.
    Do this in the pre script because it influences the automatic calculation
    of the computed fields wrt. invoicing """
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state', [
            ('waiting_date', 'sale'), ('progress', 'sale'),
            ('manual', 'sale'), ('shipping_except', 'sale'),
            ('invoice_except', 'sale')],
        table='sale_order')
    cr.execute("""
        UPDATE sale_order_line sol
        SET state = so.state
        FROM sale_order so
        WHERE sol.order_id = so.id""")


def backup_fields_sale_order(cr):
    '''
    Metodo para respaldar campos funcionales de la tabla sale_order
    '''
    column_copies_so = {
                    'sale_order': [
                        ('amount_untaxed', None, None),
                        ('amount_total', None, None),
                        ('amount_tax', None, None),
                    ],
                    }
    openupgrade.copy_columns(cr, column_copies_so)


def backup_fields_sale_order_line(cr):
    '''
    Metodo para respaldar campos funcionales de la tabla sale_order_line
    '''
    column_copies_sol = {
                    'sale_order_line': [
                        ('discount', None, None),
                        ('price_unit', None, None),
                    ],
                    }
    openupgrade.copy_columns(cr, column_copies_sol)


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(cr, field_renames)
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
    map_order_state(cr)
    backup_fields_sale_order(cr)
    backup_fields_sale_order_line(cr)
