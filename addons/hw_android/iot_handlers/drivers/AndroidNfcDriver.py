# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import json
import logging
import time
from pathlib import Path
from threading import Lock

import urllib3

from odoo import _, fields, http
from odoo.addons.hw_drivers.controllers.proxy import proxy_drivers
from odoo.addons.hw_drivers.driver import Driver
from odoo.addons.hw_drivers.event_manager import event_manager
from odoo.addons.hw_drivers.main import iot_devices
from odoo.addons.hw_drivers.tools import helpers
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

_logger = logging.getLogger(__name__)


class MyHandler(FileSystemEventHandler):
    def __init__(self, driver):
        super(MyHandler).__init__()
        _logger.info("Init")
        self.driver = driver

    def on_modified(self, event):
        data = {}
        file_path = Path.home() / 'android-nfc-scans.log'
        if file_path.exists():
            try:
                raw_json = file_path.read_text()
                data = json.loads(raw_json)
            except Exception:
                _logger.error("Malformed file: android-nfc-scans.log")
        values = data.get(self.driver.device_identifier)
        if values:
            # TODO: Decrypt the tag once we have the decryption logic
            tag = values['tag']
            timestamp = fields.Datetime.to_datetime(values['time'])
            timestamp = datetime.datetime.timestamp(timestamp)
            if timestamp > time.time() - 5:
                self.driver.data['value'] = tag
                event_manager.device_changed(self.driver)


class AndroidNFCDriver(Driver):
    connection_type = 'android'
    available_layouts = []

    def __init__(self, identifier, device_dict):
        super(AndroidNFCDriver, self).__init__(identifier, device_dict)
        self.device_connection = 'network'
        self.device_name = self._set_name()
        self.device_type = 'android'
        self.observer = False
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
                _logger.error('A error encountered : %s ', e)

    def _set_name(self):
        return _('Android: %s') % self.device_identifier

    def run(self):
        try:
            _logger.info("Watchdog setup")
            if not self.observer:
                event_handler = MyHandler(self)
                self.observer = Observer()
                _logger.info("Setup observer")
                file_path = Path.home() / 'android-nfc-scans.log'
                if not file_path.exists():
                    helpers.write_file('android-nfc-scans.log', json.dumps({}))
                self.observer.schedule(event_handler,  path=file_path._str,  recursive=False)
                self.observer.start()

                try:
                    while not self._stopped.isSet():
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.observer.stop()
                self.observer.join()
        except Exception as err:
            _logger.warning(err)

    def _action_default(self, data):
        self.data['value'] = ''
        event_manager.device_changed(self)


proxy_drivers['android'] = AndroidNFCDriver


class AndroidNFCController(http.Controller):
    @http.route('/hw_proxy/android/nfc', type='json', auth='none', cors='*')
    def scan_nfc_tag(self, android_identifier, nfc_tag, **post):
        """Here we can only save new scans made by android devices
        Here we can expect following structure:
            {
                'identifier': {'tag': 'nfc_scanned_tag', 'time': 'TIME when tag was registered'}
            }
        """
        data = {}
        file_path = Path.home() / 'android-nfc-scans.log'
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
            except Exception:
                _logger.error("Malformed file: android-nfc-scans.log")

        data['nfc_%s' % android_identifier] = {
            'tag': nfc_tag,
            'time': fields.Datetime.to_string(fields.Datetime.now())
        }
        helpers.write_file('android-nfc-scans.log', json.dumps(data))
        return True

    @http.route('/hw_proxy/add/android', type='json', auth='none', cors='*')
    def add_android_nfc_reader(self, android_identifier, **post):
        """Here somehow I need to save this information send by the Android Tablet and convert it as an device"""
        if not self.validate_token(post):
            return False
        data = {}
        file_path = Path.home() / 'android-devices.conf'
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
            except Exception:
                _logger.error("Malformed file: android-devices.conf")
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
