# -*- coding: utf-8 -*-
# © 2017 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)
try:
    import conekta
except (ImportError, IOError) as err:
    _logger.debug(err)


class ConektaController(http.Controller):

    @http.route('/payment/conekta/charge', type='json',
                auth='public', methods=['POST'], csrf=False)
    def charge_create(self, **post):
        request.session['conekta_token'] = post.get('token_id')
        payment_acquirer = request.env['payment.acquirer']
        conekta_acq = payment_acquirer.sudo().search(
            [('provider', '=', 'conekta')])
        conekta.api_key = conekta_acq.conekta_private_key
        params = self.create_params('conekta', post)
        try:
            conekta_res = conekta.Charge.create(params)
        except conekta.ConektaError as error:
            return error.message['message_to_purchaser']
        self.conekta_validate_data(conekta_res)
        res = {
            'result': True,
            'id': 1,
            'short_name': post.get('cc_number'),
            '3d_secure': False,
            'verified': False,
        }
        return res

    @http.route('/payment/conekta/s2s/create_json_3ds', type='json',
                auth='public', methods=['POST'], csrf=False)
    def conekta_s2s_create_json_3ds(self, verify_validity=False, **post):
        token = request.env['payment.acquirer'].browse(
            int(post.get('acquirer_id'))).s2s_process(post)
        if not token:
            res = {
                'result': False,
            }
            return res
        res = {
            'result': True,
            'id': token.id,
            'short_name': token.short_name,
        }
        if verify_validity is not False:
            token.validate()
            res['verified'] = token.verified
        return res

    @http.route('/payment/conekta/s2s/retrieve_json_3ds', type='json',
                auth='public', methods=['POST'], csrf=False)
    def conekta_s2s_retrieve_json_3ds(self, verify_validity=False, **post):
        tk_id = post.get('payment_token_id', False)
        if not tk_id:
            res = {
                'result': False,
            }
            return res
        tk = request.env['payment.token'].sudo().browse(int(tk_id))
        res = {
            'result': True,
            'id': tk.id,
            'short_name': tk.short_name,
            'verified': False,
            '3d_secure': False,
        }
        return res
