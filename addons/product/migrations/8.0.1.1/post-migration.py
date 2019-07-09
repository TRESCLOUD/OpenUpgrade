# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from itertools import groupby
from operator import itemgetter
from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID

logger = logging.getLogger('OpenUpgrade.product')


def load_data(cr):
    openupgrade.load_data(cr, 'product',
                          'migrations/8.0.1.1/modified_data.xml',
                          mode='init')


def migrate_packaging(cr, pool):
    """create 1 product UL for each different product packaging dimension
    and link it to the packagings
    """
    ul_obj = pool['product.ul']
    execute = openupgrade.logged_query
    legacy_columns = dict((key, openupgrade.get_legacy_name(key))
                          for key in ('height', 'width',
                                      'length', 'weight_ul'))
    execute(cr,
            'select ul, %(height)s, %(width)s, %(length)s, %(weight_ul)s '
            'from product_packaging' % legacy_columns)
    for ul_id, height, width, length, weight in cr.fetchall():
        ul_obj.write(cr, SUPERUSER_ID, [ul_id],
                     {'height': height,
                      'width': width,
                      'length': length,
                      'weight': weight,
                      })


def create_properties(cr, pool):
    """ Fields moved to properties (standard_price).

    Write using the ORM so the prices will be written as properties.
    """
    template_obj = pool['product.template']
    sql = ("SELECT id, %s FROM product_template" %
           openupgrade.get_legacy_name('standard_price'))
    cr.execute(sql)
    logger.info(
        "Creating product_template.standard_price properties"
        " for %d products." % (cr.rowcount))
    for template_id, std_price in cr.fetchall():
        template_obj.write(cr, SUPERUSER_ID, [template_id],
                           {'standard_price': std_price})
    # make properties global
    sql = ("""
        UPDATE ir_property
        SET company_id = null
        WHERE res_id like 'product.template,%%'
        AND name = 'standard_price'""")
    openupgrade.logged_query(cr, sql)

    # Affect history to the template's company
    # Note, for the time being, in a multi company context the history will
    # be incomplete for products  that don't belong to a given company
    # (Global products), because the history will be associated to the
    # company of the SUPERUSER, during the migration
    cr.execute("""
        UPDATE product_price_history pph
        SET company_id = product_template.company_id
        FROM product_template
        WHERE pph.product_template_id = product_template.id
        AND product_template.company_id IS NOT NULL
    """)

    # product.price.history entries have been generated with a value for
    # today, we want a value for the past as well, write a bogus date to
    # be sure that we have an historic value whenever we want
    cr.execute("UPDATE product_price_history SET "
               "datetime = '1970-01-01 00:00:00+00'")


def migrate_variants(cr, pool):
    template_obj = pool['product.template']
    attribute_obj = pool['product.attribute']
    attribute_value_obj = pool['product.attribute.value']
    attribute_line_obj = pool['product.attribute.line']
    fields = {'variant': openupgrade.get_legacy_name('variants'),
              'price': openupgrade.get_legacy_name('price_extra')}
    sql = ("SELECT id, %(variant)s, %(price)s, default_code, product_tmpl_id "
           "FROM product_product "
           "WHERE %(variant)s IS NOT NULL AND %(variant)s != '' "
           "OR %(price)s IS NOT NULL AND %(price)s <> 0"
           "ORDER BY product_tmpl_id, id" % fields)
    cr.execute(sql)
    rows = cr.dictfetchall()
    for tmpl_id, variants in groupby(rows, key=itemgetter('product_tmpl_id')):
        # create an attribute shared by all the variants
        template = template_obj.browse(cr, SUPERUSER_ID, tmpl_id)
        attr_id = attribute_obj.create(cr, SUPERUSER_ID,
                                       {'name': template.name})
        for variant in variants:
            # create an attribute value for this variant
            price_extra = variant[fields['price']] or 0
            name = variant[fields['variant']]
            # active_id needed to create the 'product.attribute.price'
            ctx = {'active_id': tmpl_id}
            values = {
                'name': name or variant['default_code'] or
                '%.2f' % price_extra,
                'attribute_id': attr_id,
                'product_ids': [(6, 0, [variant['id']])],
                # a 'product.attribute.price' is created when we write
                # a price_extra on an attribute value
                'price_extra': price_extra,
            }
            value_id = attribute_value_obj.create(cr, SUPERUSER_ID, values,
                                                  context=ctx)
            values = {'product_tmpl_id': tmpl_id,
                      'attribute_id': attr_id,
                      'value_ids': [(6, 0, [value_id])]}
            attribute_line_obj.create(cr, SUPERUSER_ID, values)


def active_field_template_func(cr, pool, id, vals):
    return any(vals)


################################################################################
def image_product_move_field_m2o(
        cr, pool,
        registry_old_model, field_old_model, m2o_field_old_model,
        registry_new_model, field_new_model,
        quick_request=True, compute_func=None, binary_field=False):
    """
    FUNCION ORIGINAL DE OPENUPGRADE, MODIFICADO POR TRESCLOUD:
    
    Permite eliminar imagenes que el servidor de migracion detecta como error
    en ciertos productos, esto por que el formato usado fue jpg en vez de png
    
    Use that function in the following case:
    A field moves from a model A to the model B with : A -> m2o -> B.
    (For exemple product_product -> product_template)
    This function manage the migration of this field.
    available on post script migration.
    :param registry_old_model: registry of the model A;
    :param field_old_model: name of the field to move in model A;
    :param m2o_field_old_model: name of the field of the table of the model A \
    that link model A to model B;
    :param registry_new_model: registry of the model B;
    :param field_new_model: name of the field to move in model B;
    :param quick_request: Set to False, if you want to use write function to \
    update value; Otherwise, the function will use UPDATE SQL request;
    :param compute_func: This a function that receives 4 parameters: \
    cr, pool: common args;\
    id: id of the instance of Model B\
    vals:  list of different values.\
    This function must return a unique value that will be set to the\
    instance of Model B which id is 'id' param;\
    If compute_func is not set, the algorithm will take the value that\
    is the most present in vals.\
    :binary_field: Set to True if the migrated field is a binary field

    .. versionadded:: 8.0
    """
    def default_func(cr, pool, id, vals):
        """This function return the value the most present in vals."""
        quantity = {}.fromkeys(set(vals), 0)
        for val in vals:
            quantity[val] += 1
        res = vals[0]
        for val in vals:
            if quantity[res] < quantity[val]:
                res = val
        return res

    logger.info("Moving data from '%s'.'%s' to '%s'.'%s'" % (
        registry_old_model, field_old_model,
        registry_new_model, field_new_model))

    table_old_model = pool[registry_old_model]._table
    table_new_model = pool[registry_new_model]._table
    # Manage regular case (all the value are identical)
    cr.execute(
        " SELECT %s"
        " FROM %s"
        " GROUP BY %s"
        " HAVING count(*) = 1;" % (
            m2o_field_old_model, table_old_model, m2o_field_old_model
        ))
    ok_ids = [x[0] for x in cr.fetchall()]
    if quick_request:
        query = (
            " UPDATE %s as new_table"
            " SET %s=("
            "    SELECT old_table.%s"
            "    FROM %s as old_table"
            "    WHERE old_table.%s=new_table.id"
            "    LIMIT 1) "
            " WHERE id in %%s" % (
                table_new_model, field_new_model, field_old_model,
                table_old_model, m2o_field_old_model))
        logged_query(cr, query, [tuple(ok_ids)])
    else:
        query = (
            " SELECT %s, %s"
            " FROM %s "
            " WHERE %s in %%s"
            " GROUP BY %s, %s" % (
                m2o_field_old_model, field_old_model, table_old_model,
                m2o_field_old_model, m2o_field_old_model, field_old_model))
        cr.execute(query, [tuple(ok_ids)])
        for res in cr.fetchall():
            if res[1] and binary_field:
                try:
                    pool[registry_new_model].write(
                        cr, SUPERUSER_ID, res[0],
                        {field_new_model: res[1][:]})
                except:
                    logger.info("Imagen de producto con problemas: %s", (str(res),))
            else:
                pool[registry_new_model].write(
                    cr, SUPERUSER_ID, res[0],
                    {field_new_model: res[1]})

    # Manage non-determinist case (some values are different)
    func = compute_func if compute_func else default_func
    cr.execute(
        " SELECT %s "
        " FROM %s "
        " GROUP BY %s having count(*) != 1;" % (
            m2o_field_old_model, table_old_model, m2o_field_old_model
        ))
    ko_ids = [x[0] for x in cr.fetchall()]
    for ko_id in ko_ids:
        query = (
            " SELECT %s"
            " FROM %s"
            " WHERE %s = %s;" % (
                field_old_model, table_old_model, m2o_field_old_model, ko_id))
        cr.execute(query)
        if binary_field:
            vals = [str(x[0][:]) if x[0] else False for x in cr.fetchall()]
        else:
            vals = [x[0] for x in cr.fetchall()]
        value = func(cr, pool, ko_id, vals)
        if quick_request:
            query = (
                " UPDATE %s"
                " SET %s=%%s"
                " WHERE id = %%s" % (table_new_model, field_new_model))
            logged_query(
                cr, query, (value, ko_id))
        else:
            pool[registry_new_model].write(
                cr, SUPERUSER_ID, [ko_id],
                {field_new_model: value})
################################################################################


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    get_legacy_name = openupgrade.get_legacy_name
    openupgrade.move_field_m2o(
        cr, pool,
        'product.product', get_legacy_name('color'), 'product_tmpl_id',
        'product.template', 'color')
    image_product_move_field_m2o(
        cr, pool,
        'product.product', 'image_variant', 'product_tmpl_id',
        'product.template', 'image',
        quick_request=False, binary_field=True)
    openupgrade.move_field_m2o(
        cr, pool,
        'product.product', 'active', 'product_tmpl_id',
        'product.template', 'active',
        compute_func=active_field_template_func)
    migrate_packaging(cr, pool)
    create_properties(cr, pool)
    migrate_variants(cr, pool)
    load_data(cr)
