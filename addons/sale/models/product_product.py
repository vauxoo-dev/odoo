# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _sales_count(self):
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return
        domain = [
            ('state', 'in', ['sale', 'done']),
            ('product_id', 'in', self.ids),
        ]
        sale_line_datas = self.env['sale.order.line'].read_group(
            domain, ['product_id', 'product_uom', 'product_uom_qty'],
            ['product_id', 'product_uom'], lazy=False)

        uoms = self.env['product.uom']
        products = self.env['product.product']
        prefetch = self._prefetch
        for sale_line_data in sale_line_datas:
            # Fill prefetch with all the ids to get its data using one query
            product_ids |= products.browse(
                sale_line_data['product_id'][0], prefetch=prefetch)
            uoms |= uoms.browse(
                    sale_line_data['product_uom'][0], prefetch=prefetch)

        self.update({'sales_count': 0})
        for sale_line_data in sale_line_datas:
            product = products.browse(sale_line_data['product_id'][0], prefetch=prefetch)
            uom = uoms.browse(sale_line_data['product_uom'][0], prefetch=prefetch)
            if uom != product.uom_id:
                sale_line_data['product_uom_qty'] = uom._compute_quantity(
                    sale_line_data['product_uom_qty'], product.uom_id)
            product['sales_count'] += sale_line_data['product_uom_qty']

    sales_count = fields.Integer(compute='_sales_count', string='# Sales')

    def _get_invoice_policy(self):
        return self.invoice_policy
