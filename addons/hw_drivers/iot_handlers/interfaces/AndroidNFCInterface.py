# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from pathlib import Path

from odoo.addons.hw_drivers.interface import Interface

_logger = logging.getLogger(__name__)


class AndroidNFCInterface(Interface):
    connection_type = 'android'

    def get_devices(self):
        nfc_devices = {}
        file_path = Path.home() / 'android-devices.conf'
        if file_path.exists():
            data = json.loads(file_path.read_text())
        else:
            data = {}
        for key, value in data.items():
            identifier = "nfc_%s" % key
            iot_device = {
                key: value,
            }
            nfc_devices[identifier] = iot_device
        return nfc_devices
