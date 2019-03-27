# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.logging()
def migracion_impuestos_compras(cr):  
    '''
    Metodo para migrar los impuestos de las ordenes de compra
    siempre que la tabla purchase_order_taxe exista
    '''
    if openupgrade.table_exists(cr, 'purchase_order_taxe'):
        cr.execute(
            """
            INSERT INTO account_tax_purchase_order_line_rel(
            purchase_order_line_id, account_tax_id)
            select ord_id, tax_id from purchase_order_taxe
            """)

@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.load_data(
        cr, 'purchase', 'migrations/10.0.1.2/noupdate_changes.xml',
    )
    migracion_impuestos_compras(cr)
