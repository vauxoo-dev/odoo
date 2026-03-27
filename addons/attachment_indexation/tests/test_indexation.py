# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_open
from unittest import skipIf
import os
import base64

directory = os.path.dirname(__file__)

try:
    from pdfminer.pdfinterp import PDFResourceManager
except ImportError:
    PDFResourceManager = None


@tagged('post_install', '-at_install')
class TestCaseIndexation(TransactionCase):

    @skipIf(PDFResourceManager is None, "pdfminer not installed")
    def test_attachment_pdf_indexation(self):
        with file_open(os.path.join(directory, 'files', 'test_content.pdf'), 'rb') as file:
            pdf = file.read()
            text = self.env['ir.attachment']._index(pdf, 'application/pdf')
            self.assertEqual(text, 'TestContent!!', 'the index content should be correct')

    @skipIf(PDFResourceManager is None, "pdfminer not installed")
    def test_copy_reuses_index_content(self):
        with file_open(os.path.join(directory, 'files', 'test_content.pdf'), 'rb') as file:
            pdf = file.read()
        attachment = self.env['ir.attachment'].create({
            'name': 'copy-test',
            'type': 'binary',
            'datas': base64.b64encode(pdf).decode(),
        })
        self.assertEqual(attachment.index_content, 'TestContent!!', 'ensure initial index matches expectation')
        attachment.write({'index_content': 'cached-copy-value'})
        copied = attachment.copy()
        self.assertEqual(copied.index_content, 'cached-copy-value', 'copy should preserve cached index content')
