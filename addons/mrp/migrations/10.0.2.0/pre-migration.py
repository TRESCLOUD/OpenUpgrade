# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # create an xmlid for mail.bounce.alias is it exists
    cr.execute(
        """SELECT * FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'mrp_workorder'"""
    )
    record = cr.fetchall()
    if record:
            cr.execute(
            """DROP VIEW mrp_workorder"""
        )    