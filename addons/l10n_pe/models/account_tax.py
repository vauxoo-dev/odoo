# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccoutnTax(models.Model):
    _inherit = "account.tax"

    l10n_pe_edi_tax_code = fields.Selection([
        ('1000', 'IGV - General Sales Tax'),
        ('1016', 'IVAP - Tax on Sale Paddy Rice'),
        ('2000', 'ISC - Selective Excise Tax'),
        ('9995', 'EXP - Exportation'),
        ('9996', 'GRA - Free'),
        ('9997', 'EXO - Exonerated'),
        ('9998', 'INA - Unaffected'),
        ('9999', 'OTROS - Other taxes')
    ], 'EDI peruvian code')
