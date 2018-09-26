# -*- coding: utf-8 -*-
# © 2017 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    # payment_tx_status = fields.Boolean(compute='_compute_payment_tx_status')

    # @api.depends('payment_tx_id')
    def _compute_payment_tx_status(self):
        for rec in self:
            state_done = bool(rec.payment_tx_id.state == 'done')
            provider_conekta = bool(
                rec.payment_tx_id.acquirer_id.provider == 'conekta')
            rec.payment_tx_status = False
            if rec.payment_tx_id and state_done and provider_conekta:
                rec.payment_tx_status = True
