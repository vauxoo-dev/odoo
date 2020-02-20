# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged


@tagged('reference_cache')
class TestReferenceCache(TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = self.env['test_new_api.mixed']
        self.user_demo = self.env.ref('base.user_demo')
        self.user_admin = self.env.ref('base.user_admin')

    def test_reference_cache(self):
        """test_new_api.mixed records created:
        |- id -|------ reference ----------|
        |   1  | test_new_api.model_a,1    |
        |   2  | test_new_api.model_a,2    |
        | ...  | ...                       |
        | 100  | test_new_api.model_a,100  |
        | 101  | test_new_api.model_b,1    |
        | 102  | test_new_api.model_b,2    |
        | ...  | ...                       |
        | 200  | test_new_api.model_b,100  |

        Expected cache queries executed one for each model (3 queries):
         - record.reference:
            - SELECT * FROM test_new_api_mixed WHERE id IN (id1, id2, ..., id200)
         - record.reference.name (for first record.reference of model_a):
            - SELECT * FROM test_new_api_model_a WHERE id IN (a1, a2, ..., a100)
        - record.reference.name (for first occurrence of record.reference of model_b):
            - SELECT * FROM test_new_api_model_b WHERE id IN (b1, b2, ..., b100)

        Currently it is executing the following queries (201 queries):
         - record.reference:
            - SELECT * FROM test_new_api_mixed WHERE id IN (id1, id2, ..., id200)
        - record.reference.name:
            - SELECT * FROM test_new_api_model_a WHERE id IN (a1)
            - SELECT * FROM test_new_api_model_a WHERE id IN (a2)
            - ...
            - SELECT * FROM test_new_api_model_a WHERE id IN (a100)
            - SELECT * FROM test_new_api_model_b WHERE id IN (b1)
            - SELECT * FROM test_new_api_model_b WHERE id IN (b2)
            - ...
            - SELECT * FROM test_new_api_model_b WHERE id IN (b100)
        """
        references = []
        for _ in range(100):
            references.extend([
                self.env['test_new_api.model_a'].create({'name': 'hello_a'}),
                self.env['test_new_api.model_b'].create({'name': 'hello_b'}),
            ])
        records = self.model
        for reference in references:
            records |= self.model.create({'reference': '%s,%d' % (reference._name, reference.id)})

        self.env.cache.invalidate()
        with self.assertQueryCount(3):
            # all models together
            for record in records:
                record.reference.name

        records_a = records.filtered(lambda r: 'model_a' in r.reference._name)
        records_b = records.filtered(lambda r: 'model_b' in r.reference._name)
        self.env.cache.invalidate()
        with self.assertQueryCount(1):
            # Just main model cache
            for record in records:
                record.reference
        with self.assertQueryCount(1):
            # Just model A cache
            for record in records_a:
                record.reference.name
        with self.assertQueryCount(1):
            # Just model B cache
            for record in records_b:
                record.reference.name
