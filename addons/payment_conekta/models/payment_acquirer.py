# -*- coding: utf-8 -*-
# © 2017 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
try:
    import conekta
except (ImportError, IOError) as err:
    _logger.debug(err)


class AcquirerConekta(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('conekta', 'Conekta')])
    conekta_public_key = fields.Char(required_if_provider='conekta')
    conekta_private_key = fields.Char(required_if_provider='conekta')

    @api.multi
    def conekta_get_form_action_url(self):
        self.ensure_one()
        return '/shop/payment/validate'

    @api.model
    def conekta_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'name': data['conekta_cc_number'],
            'acquirer_ref': data['token_id'],
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id'])
        })
        return payment_token

    @api.multi
    def conekta_s2s_form_validate(self, data):
        self.ensure_one()
        # mandatory fields
        for field_name in ["conekta_cc_number"]:
            if not data.get(field_name):
                return False
        return True


class PaymentTransactionStripe(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def conekta_s2s_do_transaction(self, **data):
        self.ensure_one()
        result = self._create_conekta_charge()
        return self._conekta_s2s_validate_tree(result)

    @api.multi
    def _create_conekta_charge(self):
        payment_acquirer = self.env['payment.acquirer']
        conekta_acq = payment_acquirer.sudo().search(
            [('provider', '=', 'conekta')])
        conekta.api_key = conekta_acq.conekta_private_key
        params = self._create_conekta_params('conekta')
        try:
            conekta_res = conekta.Charge.create(params)
        except conekta.ConektaError as error:
            return error
        return conekta_res

    def _create_conekta_params(self, acquirer):
        so = self.sale_order_ids.sudo()
        customer = {
            'logged_in': False,
        }
        line_items = []
        for order_line in so.order_line:
            item = {
                'name': order_line.product_id.name,
                'description': (order_line.product_id.description_sale if
                                order_line.product_id.description_sale else
                                order_line.product_id.name),
                'unit_price': int(order_line.price_unit * 100),
                'quantity': order_line.product_uom_qty,
                'sku': order_line.product_id.default_code,
                'category': order_line.product_id.categ_id.name,
            }
            line_items.append(item)
        billing_address = {
            'street1': so.partner_invoice_id.street,
            'street2': so.partner_invoice_id.street2,
            'city': so.partner_invoice_id.city,
            'state': so.partner_invoice_id.state_id.code,
            'zip': so.partner_invoice_id.zip,
            'country': so.partner_invoice_id.country_id.name,
            'tax_id': so.partner_invoice_id.vat,
            'company_name': (
                so.partner_invoice_id.parent_name or
                so.partner_invoice_id.name),
            'phone': (so.partner_invoice_id.phone
                      if so.partner_invoice_id.phone else so.company_id.phone),
            'email': so.partner_invoice_id.email,
        }
        details = {
            'billing_address': billing_address,
            'line_items': line_items,
            'name': so.partner_id.name,
            'phone': (so.partner_id.phone if
                      so.partner_id.phone else so.company_id.phone),
            'email': so.partner_id.email,
            'customer': customer,
        }
        params = {
            'description': _(
                '%s Order %s' % (so.company_id.name, so.name)),
            'amount': int(so.amount_total * 100),
            'currency': so.currency_id.name,
            'reference_id': so.name,
            'details': details,
        }
        if acquirer == 'conekta':
            params['card'] = self.payment_token_id.acquirer_ref
        return params

    @api.multi
    def _conekta_s2s_validate_tree(self, tree):
        self.ensure_one()
        if isinstance(tree, conekta.ConektaError):
            error = tree.error_json['message']
            _logger.warn(error)
            self.write({
                'state': 'error',
                'state_message': error,
                'date': fields.datetime.now(),
            })
            return False
        if tree.status == 'paid':
            self.write({
                'state': 'done',
                'date': fields.datetime.now(),
                'acquirer_reference': tree.id,
            })
            self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.active = False
            return True
        if self.state not in ('draft', 'pending', 'refunding'):
            _logger.info(
                'Conekta: trying to validate an already validated tx (ref %s)',
                self.reference)
            return True
