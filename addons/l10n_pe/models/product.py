# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    l10n_pe_gtin_id = fields.Many2one(
        'l10n_pe.product.gtin', 'Code GTIN',
        help='This field code is needed for the GTIN in the XML for SUNAT.'
        'This fields are taken directly from the Catalog N.° 25')


class ProductGTIN(models.Model):
    _name = 'l10n_pe.product.gtin'
    _description = 'Product code and name from SUNAT catalog of products'

    code = fields.Char(help="Code given by SUNAT to identify this product category", required=True)
    name = fields.Char(help="Name defined from the Catalog N.° 25 for products", required=True)

    def name_get(self):
        result = []
        for prod in self:
            result.append((prod.id, "%s %s" % (prod.code, prod.name or '')))
        return result
