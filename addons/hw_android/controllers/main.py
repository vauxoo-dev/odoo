import json
import logging

from odoo import http
from odoo.addons.iot.controllers.main import IoTController

_logger = logging.getLogger(__name__)


class AssaController(IoTController):

    @http.route('/iot/assa/connect', type='json', auth='public', csrf=False, save_session=False)
    def create_session(self, **post):
        """We need to receive some identifiers set on the iot, toket, ddb uid, devices identifier
        Then validate such information then return credential to connect to
        ASSA web api, credential stored on ir.config_parammeter
        """
        # TODO:
        if self.check_credentials(**post):

            data = {
                'username': 'sym',
                'password': 'sym',
                'vl_visionline_host': 'vl_visionline_host',
                'vl_description': 'vl_description',
            }
            return json.dumps(data)
        return json.dumps({})

    def check_credentials(self, **post):
        _logger.info("%s", repr(post))
