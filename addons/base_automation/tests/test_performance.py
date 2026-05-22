import logging

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import TransactionCaseWithUserDemo

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestBaseAutomationQueryCount(TransactionCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner_model = cls.env.ref("base.model_res_partner")

        field_ref = cls.env.ref("base.field_res_partner__ref")
        field_country = cls.env.ref("base.field_res_partner__country_id")

        cls.mx = cls.env.ref("base.mx")
        cls.us = cls.env.ref("base.us")

        # iniciar NO MX
        cls.partner = cls.env["res.partner"].create(
            {
                "country_id": cls.us.id,
                "name": "Test self.partner",
                "ref": "original",
            }
        )

        cls.automation = cls.env["base.automation"].create(
            {
                "active": True,
                "filter_domain": "[('country_code', '=', 'MX')]",
                "filter_pre_domain": "[('active', '=', True)]",
                "model_id": partner_model.id,
                "name": "Test MX Automation",
                "trigger_field_ids": [Command.link(field_country.id)],
                "trigger": "on_create_or_write",
            }
        )

        update_action = cls.env["ir.actions.server"].create(
            {
                "base_automation_id": cls.automation.id,
                "evaluation_type": "value",
                "model_id": partner_model.id,
                "name": "Update Contact",
                "state": "object_write",
                "update_field_id": field_ref.id,
                "update_path": "ref",
                "value": "test mx",
            }
        )
        update_action.flush_recordset()
        cls.automation.write({"action_server_ids": [Command.link(update_action.id)]})

    def test_base_automation_overhead(self):
        # warmup cache
        self.partner.write({"name": "Warmup", "ref": None})
        self.env.flush_all()

        # -----------------------------
        # WITHOUT AUTOMATION
        # -----------------------------
        self.automation.active = False
        self.env.clear()

        with self.assertQueryCount(__system__=15):
            _logger.info("Starting writing mx with archived automation...")
            self.partner.write({"country_id": self.mx.id})
            self.env.flush_all()
        _logger.info("...ending writing mx with archived automation")
        self.assertFalse(self.partner.ref)

        # reset
        self.partner.write({"country_id": self.us.id, "ref": "original"})
        self.env.flush_all()
        self.assertEqual(self.partner.ref, "original")

        # -----------------------------
        # WITH AUTOMATION
        # -----------------------------
        self.automation.active = True
        self.env.clear()

        with self.assertQueryCount(__system__=20):
            _logger.info("Starting writing mx with active automation...")
            self.partner.write({"country_id": self.mx.id})
            self.env.flush_all()
        _logger.info("...ending writing mx with active automation")
        self.assertEqual(self.partner.ref, "test mx")
