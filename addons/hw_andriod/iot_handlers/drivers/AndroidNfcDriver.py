# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import logging
import time
import urllib3
from pathlib import Path
from threading import Lock

from odoo import http, _, fields
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
        self.device_connection = 'network'
        self.device_name = self._set_name()
        # TODO: Not sure this is necessary
        self.device_type = 'android'
        self.read_nfc_lock = Lock()

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
        status = 'connected' if any(iot_devices[d].device_type == "android" for d in iot_devices) else 'disconnected'
        return {'status': status, 'messages': ''}

    @classmethod
    def send_layouts_list(cls):
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
        return _('Android: %s') % self.device_identifier

    def run(self):
        try:
            while not self._stopped.isSet():
                data = {}
                file_path = Path.home() / 'android-nfc-scans.conf'
                if file_path.exists():
                    raw_json = file_path.read_text()
                    if not raw_json:
                        continue
                    data = json.loads(raw_json)
                for andriod_id, values in data.items():
                    timestamp = fields.Datetime.to_datetime(values['time'])
                    timestamp = datetime.datetime.timestamp(timestamp)
                if timestamp > time.time() - 5:
                    event_manager.device_changed(self)
        except Exception as err:
            print("%s" % repr(err))
            _logger.warning(err)

    def _action_default(self, data):
        self.data['value'] = ''
        event_manager.device_changed(self)

    def read_next_nfc_tag(self):
        """Get the value of the last nfc tag that was scanned but not sent yet
        and not older than 5 seconds.
        """
        with self.read_nfc_lock:
            try:
                data = {}
                file_path = Path.home() / 'android-nfc-scans.conf'
                if file_path.exists():
                    data = json.loads(file_path.read_text())
                for andriod_id, values in data.items():
                    tag = values['tag']
                    timestamp = fields.Datetime.to_datetime(values['time'])
                    timestamp = datetime.datetime.timestamp(timestamp)
                if timestamp > time.time() - 5:
                    return tag
            except Exception:
                return ''


proxy_drivers['android'] = AndroidNFCDriver


class AndroidNFCController(http.Controller):
    @http.route('/hw_proxy/nfc', type='json', auth='none', cors='*')
    def get_nfc_tag(self):
        android = [iot_devices[d] for d in iot_devices if iot_devices[d].device_type == "android"]
        if android:
            return android[0].read_next_nfc_tag()
        time.sleep(5)
        return None

    @http.route('/hw_proxy/android/nfc', type='json', auth='none', cors='*')
    def scan_nfc_tag(self, android_identifier, nfc_tag, **post):
        """Here we can expect following structure:
            {
            'identifier': {'tag': 'nfc_scanned_tag', 'time': 'TIME when tag was registered'}
            }
        """
        # TODO: Remove this loggers, they are here because debugging
        _logger.info("%s" % repr(post))
        _logger.info("nfc_%s" % repr(android_identifier))
        _logger.info("%s" % repr(nfc_tag))

        file_path = Path.home() / 'android-nfc-scans.conf'
        if file_path.exists():
            data = json.loads(file_path.read_text())
        else:
            data = {}
        data['nfc_%s' % android_identifier] = {
            'tag': nfc_tag,
            'time': fields.Datetime.to_string(fields.Datetime.now())
        }
        helpers.write_file('android-nfc-scans.conf', json.dumps(data))
        return True

    @http.route('/hw_proxy/add/android', type='json', auth='none', cors='*')
    def add_android_nfc_reader(self, android_identifier, **post):
        """Here somehow I need to save this information send by the Android Tablet and convert it as an device"""
        # TODO: Remove this loggers, they are here because debugging
        _logger.info("%s" % repr(post))
        _logger.info("%s" % repr(android_identifier))

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
