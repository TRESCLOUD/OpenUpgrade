# -*- coding: utf-8 -*-
# Copyright 2017 Trescloud Cia Ltda (www.trescloud.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

#from openupgradelib import openupgrade
#from openupgradelib import openupgrade_90

#attachment_fields = {
#    'hr.employee': [
#        ('image', None),
#        ('image_medium', None),
#        ('image_small', None),
#    ],
#}


#@openupgrade.migrate(use_env=True)
#def migrate(env, version):
#    openupgrade.load_data(
#        env.cr, 'hr', 'migrations/9.0.1.1/noupdate_changes.xml'
#    )
#    openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)
