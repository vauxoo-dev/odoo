from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_android_via_proxy = fields.Boolean(compute="_compute_android_via_proxy")
    iface_android_id = fields.Many2one(
        'iot.device',
        domain="[('type', '=', 'android'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Enable nfc tag scanning with a remotely connected android "
        "device")

    @api.depends('iface_android_id')
    def _compute_android_via_proxy(self):
        for config in self:
            config.iface_android_via_proxy = config.iface_android_id.id is not False

    @api.depends('iface_printer_id', 'iface_display_id', 'iface_scanner_ids', 'iface_scale_id', 'iface_android_id')
    def _compute_iot_device_ids(self):
        res = super()._compute_iot_device_ids()
        for config in self:
            if config.is_posbox:
                config.iot_device_ids |= config.iface_android_id
        return res
