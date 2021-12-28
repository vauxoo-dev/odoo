from odoo import fields, models


class IotDevice(models.Model):
    _inherit = 'iot.device'

    type = fields.Selection(selection_add=[('android', 'Android')])
