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

    def __init__(self, identifier, device):
        super(AndroidNFCDriver, self).__init__(identifier, device)
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
        for cfg in device:
            for itf in cfg:
                if itf.bInterfaceClass == 3 and itf.bInterfaceProtocol != 2:
                    device.interface_protocol = itf.bInterfaceProtocol
                    return True
        return False

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
        try:
            manufacturer = util.get_string(self.dev, self.dev.iManufacturer)
            product = util.get_string(self.dev, self.dev.iProduct)
            return ("%s - %s") % (manufacturer, product)
        except ValueError as e:
            _logger.warning(e)
            return _('Unknown input device')

    def run(self):
        try:
            # TODO: How to get by loop the nfc readings?
            for event in self.input_device.read_loop():
                if self._stopped.isSet():
                    break
                if event.type == evdev.ecodes.EV_KEY:
                    data = evdev.categorize(event)
                elif data.keystate == 1:
                    self.key_input(data.scancode)

        except Exception as err:
            _logger.warning(err)

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
    def scan_nfc_tag(self):
        # http hook were tablet should send their tags read
        # event_manager.device_changed(self)
        scanners = [iot_devices[d] for d in iot_devices if iot_devices[d].device_type == "nfc"]
        if scanners:
            return scanners[0].read_next_nfc_tag()
        time.sleep(5)
        return None

    @http.route('/hw_proxy/add/android', type='json', auth='none', cors='*')
    def add_android_nfc_reader(self, android_identifier, **post):
        """Here somehow I need to save this information send by the Android Tablet and convert it as an device"""
        _logger.error("%s" % repr(post))
        file_path = Path.home() / 'android-devices.conf'
        if file_path.exists():
            data = json.loads(file_path.read_text())
        else:
            data = {}
        data[android_identifier] = True
        helpers.write_file('android-devices.conf', json.dumps(data))
        return "Hola"
