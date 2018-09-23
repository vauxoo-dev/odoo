# -*- coding: utf-8 -*-
# © 2017 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Payment Conekta",
    "summary": "Payment Acquirer: Conekta Implementation",
    "version": "10.0.1.0.0",
    "category": "Hidden",
    "website": "https://www.vauxoo.com/",
    "author": "Vauxoo",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
    ],
    "data": [
        "security/security.xml",
        "views/conekta.xml",
        "views/payment_acquirer_view.xml",
        "views/assets_frontend.xml",
        "wizards/conekta_refund_wizard_view.xml",
        "views/sale_order_view.xml",
        "views/payment_form.xml",
        "data/payment_acquirer_data.xml",
    ],
    "demo": [
        "demo/payment_acquirer_demo.xml",
    ],
    "external_dependencies": {
        "python": ["conekta"],
    },
}
