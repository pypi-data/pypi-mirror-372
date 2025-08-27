from odoo.exceptions import ValidationError
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestCRMLead(SCTestCase):
    def test_crm_lead_subscription_request_email(self):
        subscription_request_id = self.env.ref(
            "cooperator_somconnexio.sc_subscription_request_2_demo"
        )

        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "New Test Lead",
                    "subscription_request_id": subscription_request_id.id,
                }
            ]
        )
        self.assertEqual(crm_lead.email_from, subscription_request_id.email)

    def test_crm_lead_action_set_remesa_raise_error_without_partner(self):
        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "New Test Lead Without Partner",
                }
            ]
        )

        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: The subscription request related must be validated.".format(
                crm_lead.id
            ),
            crm_lead.action_set_remesa,
        )
