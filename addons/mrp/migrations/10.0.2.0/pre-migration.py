# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    # create an xmlid for mail.bounce.alias is it exists
    try:
        cr.execute(
            """DROP VIEW mrp_workorder"""
        )
    except:
        _logger.error('Error al borrar la vista mrp_workorder')
    