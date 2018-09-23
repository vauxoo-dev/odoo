# -*- coding: utf-8 -*-
# © 2016 Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_10_admin_checkout(self):
        self.phantom_js(
            "/",
            """odoo.__DEBUG__.services['web_tour.tour'].run(
            'shop_buy_prod_conekta')""",
            """odoo.__DEBUG__.services[
            'web_tour.tour'].tours.shop_buy_prod_conekta.ready""",
            login="admin")

    def test_20_demo_checkout(self):
        self.phantom_js(
            "/",
            """odoo.__DEBUG__.services['web_tour.tour'].run(
            'shop_buy_prod_conekta')""",
            """odoo.__DEBUG__.services[
            'web_tour.tour'].tours.shop_buy_prod_conekta.ready""",
            login="demo")

    def test_30_public_checkout(self):
        self.phantom_js(
            "/",
            """odoo.__DEBUG__.services['web_tour.tour'].run(
            'shop_buy_prod_conekta')""",
            """odoo.__DEBUG__.services[
            'web_tour.tour'].tours.shop_buy_prod_conekta.ready"""
        )
