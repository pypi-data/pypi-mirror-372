from odoo.tests.common import TransactionCase
from odoo.addons.component.tests.common import ComponentMixin


class SCTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(SCTestCase, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=True,  # no jobs thanks
            )
        )


class SCComponentTestCase(SCTestCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(SCComponentTestCase, cls).setUpClass()
        cls.setUpComponent()

    def setUp(self):
        super(SCComponentTestCase, self).setUp()
        ComponentMixin.setUp(self)
