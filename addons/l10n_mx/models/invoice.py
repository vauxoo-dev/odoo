# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Invoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_type = fields.Char(
        'Type MX', compute='_compute_l10n_mx_type',
        help='CFDI v3.2 request the field "tipoDeComprobante".\n'
        'For customer invoice is: "ingreso".\n'
        'For customer refund is: "egreso".')

    @api.one
    @api.depends('type')
    def _compute_l10n_mx_type(self):
        self.l10n_mx_type = None
        if self.type == 'out_invoice':
            self.l10n_mx_type = 'ingreso'
        elif self.type == 'out_refund':
            self.l10n_mx_type = 'egreso'
