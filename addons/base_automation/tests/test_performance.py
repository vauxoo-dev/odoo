import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestBaseAutomationQueryCount(TransactionCase):
    def setUp(self):
        super().setUp()

        self.partner_model = self.env.ref("base.model_res_partner")
        self.field_ref = self.env.ref("base.field_res_partner__ref")
        self.field_country = self.env.ref("base.field_res_partner__country_id")

        self.mx = self.env.ref("base.mx")
        self.us = self.env.ref("base.us")

        # Iniciar NO MX
        self.partner = self.env["res.partner"].create(
            {
                "country_id": self.us.id,
                "name": "Test self.partner",
                "ref": "original",
            }
        )
        self.env["base.automation"].search([("active", "=", True)]).write({"active": False})
        self.automation = self.env["base.automation"].create(
            {
                "active": False,
                "filter_domain": "[('country_id.code', '=', 'MX')]",
                "filter_pre_domain": "[('active', '=', True)]",
                "model_id": self.partner_model.id,
                "name": "Test MX Automation",
                "trigger": "on_create_or_write",
                "state": "object_write",
                "fields_lines": [
                    (
                        0,
                        0,
                        {
                            "col1": self.field_ref.id,
                            "type": "value",
                            "value": "test mx",
                        },
                    )
                ],
            }
        )

    def test_base_automation_overhead(self):
        # -----------------------------
        # 1. WITHOUT AUTOMATION
        # -----------------------------
        # Warmup inicial
        self.partner.write({"name": "Warmup", "ref": False})
        
        # Invalidate cache limpia solo la memoria de este registro, sin destruir el entorno global
        self.partner.invalidate_cache()

        # Ajusta este número al ejecutar, en v12 suele rondar entre 3 y 8 consultas
        with self.assertQueryCount(__system__=8): 
            _logger.info("Starting writing mx with NO automation...")
            self.partner.write({"country_id": self.mx.id})
        _logger.info("...ending writing mx with NO automation")
        
        # Como la automatización ni siquiera existe aún, esto pasará 100% seguro
        self.assertFalse(self.partner.ref)

        # Reset a estado original
        self.partner.write({"country_id": self.us.id, "ref": "original"})
        self.partner.invalidate_cache()
        self.assertEqual(self.partner.ref, "original")

        self.partner.write({"name": "Warmup 2", "country_id": self.us.id})
        self.partner.invalidate_cache()

        self.automation.write({"active": True})
        # Ajusta este número, debería rondar entre 8 y 15 consultas
        with self.assertQueryCount(__system__=36):
            _logger.info("Starting writing mx with active automation...")
            self.partner.write({"country_id": self.mx.id})
        _logger.info("...ending writing mx with active automation")
        
        # Ahora sí, la automatización hizo su trabajo
        self.assertEqual(self.partner.ref, "test mx")
