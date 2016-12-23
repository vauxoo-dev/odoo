# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

CER_TO_PEM_CMD = 'openssl x509 -in %s -inform der -outform pem -out %s'
KEY_TO_PEM_CMD = 'openssl pkcs8 -in %s -inform der -outform pem -out %s -passin file:%s'

def unlink_temporary_files(temporary_files):
    for temporary_file in temporary_files:
        try:
            os.unlink(temporary_file)
        except (OSError, IOError):
            _logger.error('Error when trying to remove file %s' % temporary_file)

def convert_CER_to_PEM(cer):
    cer_file_fd, cer_file_path = tempfile.mkstemp(suffix='.cer', prefix='edi.mx.tmp.')
    with closing(os.fdopen(cer_file_fd, 'w')) as cer_file:
        cer_file.write(cer)
    cerpem_file_fd, cerpem_file_path = tempfile.mkstemp(suffix='.pem', prefix='edi.mx.tmp.')

    os.popen(CER_TO_PEM_CMD % (cer_file_path, cerpem_file_path))
    with open(cerpem_file_path, 'r') as f:
        cer_pem = f.read()
    
    unlink_temporary_files([cer_file_path, cerpem_file_path])
    return cer_pem

def convert_key_CER_to_PEM(key, password):
    key_file_fd, key_file_path = tempfile.mkstemp(suffix='.key', prefix='edi.mx.tmp.')
    with closing(os.fdopen(key_file_fd, 'w')) as key_file:
        key_file.write(key)
    pwd_file_fd, pwd_file_path = tempfile.mkstemp(suffix='.txt', prefix='edi.mx.tmp.')
    with closing(os.fdopen(pwd_file_fd, 'w')) as pwd_file:
        pwd_file.write(password)
    keypem_file_fd, keypem_file_path = tempfile.mkstemp(suffix='.key', prefix='edi.mx.tmp.')

    os.popen(KEY_TO_PEM_CMD % (key_file_path, keypem_file_path, pwd_file_path))
    with open(keypem_file_path, 'r') as f:
        key_pem = f.read()

    unlink_temporary_files([key_file_path, keypem_file_path, pwd_file_path])
    return key_pem

class Certificate(models.Model):
    _name = 'l10n_mx_edi.certificate'

    certificate = fields.Binary(
        string='Certificate',
        help='Certificate in der format')
    certificate_key = fields.Binary(
        string='Certificate Key',
        help='Certificate Key in der format')
    lcertificate_password = fields.Char(
        string='Certificate Password',
        help='Password for the Certificate Key')
    available_date = fields.Date(
        string='Available date',
        readonly=True)
    expiration_date = fields.Date(
        string='Expiration date',
        readonly=True)

    api.onchange('l10n_mx_edi_cer', 'l10n_mx_edi_cer_key', 'l10n_mx_edi_cer_password')
    def _onchange_credentials(self):
        pass