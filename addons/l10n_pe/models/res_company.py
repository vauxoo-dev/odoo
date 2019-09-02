# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models


class ResCompany(models.Model):

    _inherit = "res.company"

    def _localization_use_documents(self):
        self.ensure_one()
        return self.country_id == self.env.ref('base.pe') or super()._localization_use_documents()
