import base64
import email
import hashlib
import hmac
# import ssl
import socket
import json
import logging
from time import gmtime, time, strftime
import requests
import urllib3

from odoo.addons.hw_drivers.tools import helpers

_logger = logging.getLogger(__name__)


class Visionline:
    vl_visionline_host = ""  # example: "https://127.0.0.1"
    vl_door = ""  # example: "101"
    vl_endpointId = ""  # example: "jilly44"
    vl_label = "%ROOMRANGE%:%UUID%:%CARDNUM%"
    vl_description = "Hotel California"
    vl_session_id = ""
    vl_access_key = ""

    def _setup_credentials_from_server(self):
        server = helpers.get_odoo_server_url()
        if server:
            subject = helpers.read_file_first_line('odoo-subject.conf')
            if subject:
                domain = helpers.get_ip().replace('.', '-') + subject.strip('*')
            else:
                domain = helpers.get_ip()
            iot_box = {
                'name': socket.gethostname(),
                'identifier': helpers.get_mac_address(),
                'ip': domain,
                'token': helpers.get_token(),
                'version': helpers.get_version(),
            }
            data = {
                'jsonrpc': 2.0,
                'params': {
                    'iot_box': iot_box,
                }
            }
            # disable certifiacte verification
            urllib3.disable_warnings()
            try:
                req = requests.post(
                    server + "/iot/assa/connect",
                    json=data, verify=False)
                result = req.json().get('result', {})
                self.vl_visionline_host = result.get('vl_visionline_host')
                self.vl_description = result.get('vl_description')
                self.username = result.get('username')
                self.password = result.get('password')

            except Exception as e:
                _logger.error('Could not reach configured server')
                _logger.error('A error encountered : %s ', e)
        else:
            _logger.warning('Odoo server not set')

    def start(self):
        self._setup_credentials_from_server()
        urllib3.disable_warnings()
        if not self.vl_visionline_host:
            _logger.error(
                "::Error Please check your initial values for vl_visionline_host")
        else:
            self.create_session()

    def create_session(self):
        _logger.info("=>Get session")
        vl_json = {'username': self.username, 'password': self.password}
        vl_api = "/api/v1/sessions"
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Date': email.utils.formatdate(time()),
            'Content-MD5': self.create_md5header(vl_json)
        }

        json_body = json.dumps(vl_json).encode('utf-8')
        url = "%s%s" % (self.vl_visionline_host, vl_api)
        response = requests.post(url, headers=headers, data=json_body, verify=False)

        if response.status_code == 201:
            self.vl_session_id = response.json().get('id')
            self.vl_access_key = response.json().get('accessKey')
            _logger.info("RESPONSE: id: %s, accessKey: %s", self.vl_session_id, self.vl_access_key)
        else:
            _logger.error("Something went wrong....")

    def create_key(self):
        """This is an example how to create a card Key"""
        _logger.info("=>Create key")
        exp_time = gmtime(time()+(60*60*24))
        expire_time = strftime("%Y%m%dT%H%M", exp_time)
        vl_api = "/api/v1/cards?action=mobileAccess&override=true"
        vl_json = {
            'expire_time': expire_time,
            'format': 'rfid48',
            'endPointID': self.vl_endpointId,
            'label': self.vl_label,
            'description': self.vl_description,
            'doorOperations': [{'doors': [self.vl_door], 'operation':'guest'}]
        }
        date_time = email.utils.formatdate(time())
        string_to_sign = "POST\n"
        string_to_sign += "{}\n".format(self.create_md5header(vl_json))
        string_to_sign += "{}\n".format('application/json;charset=utf-8')
        string_to_sign += "{}\n".format(date_time)
        string_to_sign += vl_api

        hash_code = hmac.new(self.vl_access_key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1)
        sign_res = base64.b64encode(hash_code.digest()).decode('utf-8')

        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Date': email.utils.formatdate(time()),
            'Content-MD5': self.create_md5header(vl_json),
            'Authorization': 'AWS %s:%s' % (self.vl_session_id, sign_res)
        }

        json_body = json.dumps(vl_json).encode('utf-8')
        response = requests.post(self.vl_visionline_host+vl_api, headers=headers, data=json_body, verify=False)

        if response.status_code == 201:
            _logger.info("RESPONSE: Key created")
        else:
            _logger.info(response.content)
            _logger.info("Something went wrong creating the key....")

        self.delete_session()

    def delete_session(self):
        _logger.info("=>Delete Session")
        if not self.vl_access_key or not self.vl_session_id:
            return
        vl_api = "/api/v1/sessions/"+self.vl_session_id
        date_time = email.utils.formatdate(time())
        string_to_sign = "DELETE\n"
        string_to_sign += "\n"
        string_to_sign += "\n"
        string_to_sign += "{}\n".format(date_time)
        string_to_sign += vl_api
        hash_code = hmac.new(
            self.vl_access_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1)
        sign_res = base64.b64encode(hash_code.digest()).decode('utf-8')
        headers = {
            'Date': email.utils.formatdate(time()),
            'Authorization': 'AWS %s:%s' % (self.vl_session_id, sign_res)
        }
        response = requests.delete(
            self.vl_visionline_host+vl_api,
            headers=headers, verify=False)

        if response.status_code == 201:
            _logger.info("RESPONSE: Session deleted")
            self.vl_session_id = ""
            self.vl_access_key = ""
        else:
            _logger.info("Something went wrong deleting the session....")

    def create_md5header(self, val):
        hash_code = hashlib.new('md5')
        hash_code.update(json.dumps(val).encode('utf-8'))
        res = base64.b64encode(hash_code.digest())
        return res.decode('utf-8')

    def decode_tag(self, tag):
        try:
            self.start()
            # implement decode request
            return tag
        except Exception as e:
            return "Malformed TAG %s" % str(e)
        finally:
            self.delete_session()
