# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    clabe = fields.Char('CLABE',
                        help="More info wikipedia.org/wiki/CLABE")
    last_acc_number = fields.Char('Last 4 digits',
                                  compute='_compute_last_acc_number',
                                  help="CFDI v3.2 request the last 4 digits of"
                                  " a bank account number for the field "
                                  "'NumCtaPago' of xml.")

    @api.one
    @api.depends('acc_number')
    def _compute_last_acc_number(self):
        acc = ''.join([s for s in (self.acc_number or '') if s.isdigit()])[-4:]
        self.last_acc_number = acc if len(acc) == 4 else None
