# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright 2019 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>

from odoo import fields, models


class City(models.Model):
    _inherit = "res.city"

    l10n_pe_code = fields.Char('Code', help='This code will help with the '
                               'identification of each city in Peru.')
