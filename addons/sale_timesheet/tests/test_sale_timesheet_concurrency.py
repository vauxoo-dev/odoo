from odoo import api
from odoo.tests import Form, TransactionCase, tagged


@tagged("timesheet_concurrency")
class TestTimesheetConcurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task = cls.env.ref("sale_timesheet.project_task_internal")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.task_form_view = cls.env.ref("project.view_task_form2")

    def create_timesheet(self, env):
        """Create timesheet records with particular env from the form task view"""
        task = self.task.with_env(env)
        task_form_view = self.task_form_view.with_env(env)
        with Form(task, task_form_view) as task_form:
            with task_form.timesheet_ids.new() as line:
                line.name = "Testing"
                line.unit_amount = 3
        task = task_form.save()
        return task

    def test_timesheet_concurrency(self):
        """Create timesheet records from 2 different users concurrently for the same task
        in order to catch concurrency issues"""
        with self.env.registry.cursor() as cr1, self.env.registry.cursor() as cr2:
            # Avoid waiting for a long time if the record is locked
            timeout_query = "SET LOCAL statement_timeout = '15s'"
            cr1.execute(timeout_query)
            cr2.execute(timeout_query)

            env_demo = api.Environment(cr1, self.user_demo.id, {})
            self.create_timesheet(env_demo)

            env_admin = api.Environment(cr2, self.user_admin.id, {})
            self.create_timesheet(env_admin)
