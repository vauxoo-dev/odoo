# Part of Odoo. See LICENSE file for full copyright and licensing details.

import evdev
import json
import logging
import time
import urllib3
from usb import util
from pathlib import Path

from odoo import http, _
from odoo.addons.hw_drivers.controllers.proxy import proxy_drivers
from odoo.addons.hw_drivers.driver import Driver
from odoo.addons.hw_drivers.event_manager import event_manager
from odoo.addons.hw_drivers.main import iot_devices
from odoo.addons.hw_drivers.tools import helpers

_logger = logging.getLogger(__name__)


class AndroidNFCDriver(Driver):
    connection_type = 'android'
    available_layouts = []

    def __init__(self, identifier, device_dict):
        super(AndroidNFCDriver, self).__init__(identifier, device_dict)
        self.device_connection = 'direct'
        self.device_name = self._set_name()

        self._actions.update({
            '': self._action_default,
        })

    @classmethod
    def supported(cls, device):
        """This method is meant to say if the tablet is supported, here can
        implement Android Versions verifications.
        Used on hw_drivers/interface.py when updating devices.
        """
        # TODO: implement
        return True

    @classmethod
    def get_status(self):
        """Allows `hw_proxy.Proxy` to retrieve the status of the scanners"""
        status = 'connected' if any(iot_devices[d].device_type == "nfc" for d in iot_devices) else 'disconnected'
        return {'status': status, 'messages': ''}

    @classmethod
    def send_layouts_list(cls):
        # Reuse this to notify Odoo about new drivers
        server = helpers.get_odoo_server_url()
        if server:
            urllib3.disable_warnings()
            pm = urllib3.PoolManager(cert_reqs='CERT_NONE')
            server = server + '/iot/nfc_layouts'
            try:
                pm.request('POST', server, fields={'available_layouts': json.dumps(cls.available_layouts)})
            except Exception as e:
                _logger.error('Could not reach configured server')
                _logger.error('A error encountered : %s ' % e)

    def _set_name(self):
        # TODO: implement
        # self.dev is a dict that is get from get_devices from Android Interface
        return _('Android Unknown input device')

    def _action_default(self, data):
        self.data['value'] = ''
        event_manager.device_changed(self)

    def read_next_nfc_tag(self):
        """Get the value of the last barcode that was scanned but not sent yet
        and not older than 5 seconds. This function is used in Community, when
        we don't have access to the IoTLongpolling.

        Returns:
            str: The next barcode to be read or an empty string.
        """
        # TODO: Implement reading nfc already sent by Android NFC readers

        # Previous query still running, stop it by sending a fake barcode
        if self.read_barcode_lock.locked():
            self._barcodes.put((time.time(), ""))

        with self.read_barcode_lock:
            try:
                timestamp, barcode = self._barcodes.get(True, 55)
                if timestamp > time.time() - 5:
                    return barcode
            except Exception:
                return ''


proxy_drivers['android'] = AndroidNFCDriver


class AndroidNFCController(http.Controller):
    @http.route('/hw_proxy/android', type='json', auth='none', cors='*')
    def get_nfc_tag(self):
        # Provide Nfc tags already scanned
        scanners = [iot_devices[d] for d in iot_devices if iot_devices[d].device_type == "nfc"]
        if scanners:
            return scanners[0].read_next_nfc_tag()
        time.sleep(5)
        return None

    @http.route('/hw_proxy/android/nfc', type='json', auth='none', cors='*')
    def scan_nfc_tag(self, android_identifier, nfc_tag, **post):
        """Here we can expect following structure:
            {
                'identifier': 'nfc_tag_value'
            }
        """
        _logger.error("%s" % repr(post))
        _logger.error("%s" % repr(android_identifier))
        _logger.error("%s" % repr(nfc_tag))
        # http hook were tablet should send their tags read
        # self.data['value'] = ''
        # event_manager.device_changed(self)

        file_path = Path.home() / 'android-nfc-scans.conf'
        if file_path.exists():
            data = json.loads(file_path.read_text())
        else:
            data = {}
        data[android_identifier] = nfc_tag
        helpers.write_file('android-nfc-scans.conf', json.dumps(data))
        return True

    @http.route('/hw_proxy/add/android', type='json', auth='none', cors='*')
    def add_android_nfc_reader(self, android_identifier, **post):
        """Here somehow I need to save this information send by the Android Tablet and convert it as an device"""
        _logger.error("%s" % repr(post))
        _logger.error("%s" % repr(android_identifier))

        if not self.validate_token(post):
            return False

        file_path = Path.home() / 'android-devices.conf'
        if file_path.exists():
            data = json.loads(file_path.read_text())
        else:
            data = {}
        if android_identifier in data:
            return True
        data[android_identifier] = True
        helpers.write_file('android-devices.conf', json.dumps(data))
        return True

    def validate_token(self, data):
        if not data.get('token') or False:
            return False
        token = data.get('token')
        db_uuid = helpers.read_file_first_line('odoo-db-uuid.conf')
        return db_uuid == token
