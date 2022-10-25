# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _

from odoo.addons.sale.controllers.portal import CustomerPortal

from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    @http.route()
    def portal_my_orders(self, *args, **kw):
        response = super().portal_my_orders(*args, **kw)

        return response